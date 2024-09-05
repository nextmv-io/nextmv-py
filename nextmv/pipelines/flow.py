import ast
import base64
import collections
import inspect
import io
import time
from typing import List, Optional, Union

from pathos.multiprocessing import ProcessingPool as Pool

from nextmv.cloud import Application, Client, StatusV2

from . import utils


class DAGNode:
    def __init__(self, step_function, step_definition, docstring):
        self.step_function = step_function
        self.step = step_definition
        self.docstring = docstring
        self.successors: List[DAGNode] = []

    def __repr__(self):
        return f"DAGNode({self.step_function.name})"


def check_cycle(nodes: List[DAGNode]):
    """
    Checks the given DAG for cycles and returns nodes that are part of a cycle.
    """
    # Step 1: Calculate in-degree (number of incoming edges) for each node
    in_degree = {node: 0 for node in nodes}

    for node in nodes:
        for successor in node.successors:
            in_degree[successor] += 1

    # Step 2: Initialize a queue with all nodes that have in-degree 0
    queue = collections.deque([node for node in nodes if in_degree[node] == 0])

    # Number of processed nodes
    processed_count = 0

    # Step 3: Process nodes with in-degree 0
    while queue:
        current_node = queue.popleft()
        processed_count += 1

        # Decrease the in-degree of each successor by 1
        for successor in current_node.successors:
            in_degree[successor] -= 1
            # If in-degree becomes 0, add it to the queue
            if in_degree[successor] == 0:
                queue.append(successor)

    # Step 4: Identify the faulty nodes (those still with in-degree > 0)
    faulty_nodes = [node for node in nodes if in_degree[node] > 0]

    # If there are faulty nodes, there's a cycle
    if faulty_nodes:
        return True, faulty_nodes
    else:
        return False, None


class FlowSpec:
    def __init__(self, name: str, input: dict, client: Optional[Client] = None):
        self.name = name
        self.graph = FlowGraph(self.__class__)
        self.client = client if client is not None else Client()
        self.input = input
        self.results = {}

    def __repr__(self):
        return f"Flow({self.name})"

    def run(self):
        open_nodes = set(self.graph.start_nodes)
        closed_nodes = set()

        # Run the nodes in parallel
        tasks = {}
        with Pool(8) as pool:
            while open_nodes:
                while True:
                    # Get the first node from the open nodes which has all its predecessors done
                    node = next(
                        iter(
                            filter(
                                lambda n: all(p in closed_nodes for p in n.predecessors),
                                open_nodes,
                            )
                        ),
                        None,
                    )
                    if node is None:
                        # No more nodes to run at this point. Wait for the remaining tasks to finish.
                        break
                    open_nodes.remove(node)
                    # Run the node asynchronously
                    tasks[node] = pool.apipe(
                        self.__run_node,
                        node,
                        self._get_inputs(node),
                        self.client,
                    )

                # Wait until at least one task is done
                task_done = False
                while not task_done:
                    time.sleep(0.1)
                    # Check if any tasks are done, if not, keep waiting
                    for node, task in list(tasks.items()):
                        if task.ready():
                            # Remove task and mark successors as ready by adding them to the open list.
                            result = task.get()
                            self.set_result(node, result)
                            del tasks[node]
                            task_done = True
                            closed_nodes.add(node)
                            open_nodes.update(node.successors)

    def set_result(self, step: callable, result: object):
        self.results[step.step] = result

    def get_result(self, step: callable) -> Union[object, None]:
        return self.results.get(step.step)

    def _get_inputs(self, node: DAGNode) -> List[object]:
        return (
            [self.get_result(predecessor) for predecessor in node.step.needs.predecessors]
            if node.step.is_needs()
            else [self.input]
        )

    @staticmethod
    def __run_node(node: DAGNode, inputs: List[object], client: Client) -> List[object] | object | None:
        utils.log(f"Running node {node.step.get_name()}")

        # Skip the node if it is optional and the condition is not met
        if node.step.skip():
            utils.log(f"Skipping node {node.step.get_name()}")
            return

        # Run the step
        if node.step.is_app():
            app_step = node.step.app
            repetitions = node.step.repeat.repetitions if node.step.is_repeat() else 1
            # Prepare the input for the app
            # TODO: We only support one predecessor for app steps for now. This may
            # change in the future. We may want to support multiple predecessors for
            # app steps. However, we need to think about how to handle the input and
            # how to expose control over the input to the user.
            if len(inputs) > 1:
                raise Exception(
                    f"App steps cannot have more than one predecessor, but {node.step.get_name()} has {len(inputs)}"
                )
            inputs = [
                (
                    [],  # No nameless arguments
                    {  # We use the named arguments to pass the user arguments to the run function
                        "input": inputs[0],
                        "options": app_step.parameters,
                    },
                )
            ] * repetitions
            app = Application(client=client, id=app_step.app_id)
            # Run the app (or multiple runs if it is a repeat step)
            run_ids = [app.new_run(*i[0], **i[1]) for i in inputs]
            outputs = utils.wait_for_runs(app=app, run_ids=run_ids)
            # Check if all runs were successful
            for output in outputs:
                if output.metadata.status_v2 != StatusV2.succeeded:
                    raise Exception(
                        f"Step {node.step.get_name()} failed with status {output.metadata.status_v2}: "
                        + f"{output.error_log}"
                    )
            # Unwrap the result and store it
            # TODO: We may want to store the full RunResult object in certain cases.
            # Maybe this can become a parameter of the step decorator.
            outputs = [output.output for output in outputs]
            return outputs if node.step.is_repeat() else outputs[0]
        else:
            spec = inspect.getfullargspec(node.step.function)
            if len(spec.args) == 0:
                output = node.step.function()
            else:
                output = node.step.function(*inputs)
            return output


class FlowGraph:
    def __init__(self, flow_spec):
        self.flow_spec = flow_spec
        self.__create_graph(flow_spec)
        self.__debug_print_graph()
        # Create a Mermaid diagram of the graph and log it
        mermaid = self.__to_mermaid()
        utils.log(mermaid)
        mermaid_url = f'https://mermaid.ink/svg/{base64.b64encode(mermaid.encode("utf8")).decode("ascii")}?theme=dark'
        utils.log(f"Mermaid URL: {mermaid_url}")

    def __create_graph(self, flow_spec):
        module = __import__(flow_spec.__module__)
        class_name = flow_spec.__name__
        tree = ast.parse(inspect.getsource(module)).body
        root = [n for n in tree if isinstance(n, ast.ClassDef) and n.name == class_name][0]

        # Build the graph
        self.nodes = []
        visitor = StepVisitor(self.nodes, flow_spec)
        visitor.visit(root)

        # Init nodes for all steps
        nodes_by_step = {node.step: node for node in self.nodes}
        for node in self.nodes:
            node.predecessors = []
            node.successors = []

        for node in self.nodes:
            if not node.step.is_needs():
                continue
            for predecessor in node.step.needs.predecessors:
                predecessor_node = nodes_by_step[predecessor.step]
                node.predecessors.append(predecessor_node)
                predecessor_node.successors.append(node)

        self.start_nodes = [node for node in self.nodes if not node.predecessors]

        # Make sure that all app steps have at most one predecessor.
        # TODO: This may change in the future. See other comment about it in this file.
        for node in self.nodes:
            if node.step.is_app() and len(node.predecessors) > 1:
                raise Exception(
                    "App steps cannot have more than one predecessor, "
                    + f"but {node.step.get_name()} has {len(node.predecessors)}"
                )

        # Check for cycles
        cycle, cycle_nodes = check_cycle(self.nodes)
        if cycle:
            raise Exception(f"Cycle detected in the flow graph, cycle nodes: {cycle_nodes}")

    def __to_mermaid(self):
        """Convert the graph to a Mermaid diagram."""
        out = io.StringIO()
        out.write("graph TD\n")
        for node in self.nodes:
            node_name = node.step.get_name()
            if node.step.is_repeat():
                out.write(f"  {node_name}{{ }}\n")
                out.write(f"  {node_name}_join{{ }}\n")
                repetitions = node.step.repeat.repetitions
                for i in range(repetitions):
                    out.write(f"  {node_name}_{i}({node_name}_{i})\n")
                    out.write(f"  {node_name} --> {node_name}_{i}\n")
                    out.write(f"  {node_name}_{i} --> {node_name}_join\n")
                for successor in node.successors:
                    out.write(f"  {node_name}_join --> {successor.step.get_name()}\n")
            else:
                out.write(f"  {node_name}({node_name})\n")
                for successor in node.successors:
                    out.write(f"  {node_name} --> {successor.step.get_name()}\n")
        return out.getvalue()

    def __debug_print_graph(self):
        for node in self.nodes:
            utils.log("Node:")
            utils.log(f"  Definition: {node.step}")
            utils.log(f"  Docstring: {node.docstring}")


class StepVisitor(ast.NodeVisitor):
    def __init__(self, nodes: List[DAGNode], flow: FlowSpec):
        self.nodes = nodes
        self.flow = flow
        super().__init__()

    def visit_FunctionDef(self, step_function):
        func = getattr(self.flow, step_function.name)
        if hasattr(func, "is_step"):
            self.nodes.append(DAGNode(step_function, func.step, func.__doc__))
