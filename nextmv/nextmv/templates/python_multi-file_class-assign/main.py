from __future__ import annotations

from typing import Any

from pyomo.environ import Binary, ConcreteModel, Constraint, Objective, Param, Set, SolverFactory, Var, maximize, value
from visualizations import generate_visual_assets

import nextmv

STANDARD_END_TIME = 15  # 3 PM


def main() -> None:
    """
    Entry point for the application.

    Loads options and input data, invokes the solver, logs progress, and
    writes the output using the nextmv framework.
    """

    loaded_input = nextmv.load(
        data_files=[nextmv.json_data_file(name="input", input_data_key="input")],
    )
    options = loaded_input.options
    input_data = loaded_input.data["input"]

    nextmv.log("Solving school class assignment problem...")
    nextmv.log(f"  Students: {len(input_data.get('students', []))}")
    nextmv.log(f"  Classes: {len(input_data.get('classes', []))}")

    solution, metrics, visual_assets = solve(input_data, options)

    nextmv.log(f"  Assigned: {solution['total_assigned']}/{solution['total_students']}")

    nextmv.write(
        metrics=metrics,
        assets=visual_assets,
        solution_files=[nextmv.json_solution_file(name="solution", data=solution)],
    )


def solve(
    input_data: dict[str, Any],
    options: nextmv.Options,
) -> tuple[dict[str, Any], dict[str, Any], list[Any]]:
    """
    Solve the school class assignment problem using Pyomo.

    Builds the MIP model, solves it with the configured solver, then extracts
    the solution, computes metrics, and generates visual assets.

    Parameters
    ----------
    input_data : dict[str, Any]
        Raw problem input containing ``students``, ``classes``, and optional
        ``separations`` keys.
    options : nextmv.Options
        Run-time options including solver name, time limit, and extended-day
        configuration values.

    Returns
    -------
    solution : dict[str, Any]
        Assignment results with keys ``assignments``, ``unassigned``,
        ``total_assigned``, and ``total_students``.
    metrics : dict[str, Any]
        Summary statistics including objective value, preference satisfaction
        rates, and solver termination information.
    visual_assets : list[Any]
        Visual asset objects produced by ``generate_visual_assets``.
    """
    students = input_data.get("students", [])
    classes = input_data.get("classes", [])
    student_data = {s["id"]: s for s in students}
    class_data = {c["id"]: c for c in classes}

    model = ConcreteModel()

    eligible_extended_day, class_ids = _build_sets_and_params(
        model, students, classes, student_data, class_data, options
    )
    _add_objective(model)
    _add_constraints(model, input_data, student_data, class_data, class_ids)

    solver = SolverFactory("highs")
    solver.options["timelimit"] = options.duration
    results = solver.solve(model, tee=False)

    solution = _extract_solution(model, student_data, class_data, eligible_extended_day, students)
    metrics = _compute_metrics(model, solution, results, student_data)
    visual_assets = generate_visual_assets(input_data, solution, metrics)

    return solution, metrics, visual_assets


def _build_sets_and_params(
    model: ConcreteModel,
    students: list[dict[str, Any]],
    classes: list[dict[str, Any]],
    student_data: dict[str, dict[str, Any]],
    class_data: dict[str, dict[str, Any]],
    options: nextmv.Options,
) -> tuple[list[str], list[str]]:
    """
    Initialize sets, parameters, and decision variables on the model.

    Populates ``model`` with Pyomo sets (``S``, ``C``, ``E``), parameters
    (``priority``, ``focus_bonus``, ``extended_day_penalty``,
    ``extended_day_bonus``, ``capacity``), and binary decision variables
    (``x``, ``y``).

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo concrete model to mutate.
    students : list[dict[str, Any]]
        List of student records, each containing at minimum an ``"id"`` key.
    classes : list[dict[str, Any]]
        List of class records, each containing at minimum an ``"id"`` key.
    student_data : dict[str, dict[str, Any]]
        Student records keyed by student ID.
    class_data : dict[str, dict[str, Any]]
        Class records keyed by class ID.
    options : nextmv.Options
        Run-time options providing ``extended_day_time``, ``extended_day_penalty``,
        and ``extended_day_bonus`` values.

    Returns
    -------
    eligible_extended_day : list[str]
        Student IDs whose extended-day request falls within the configured limit.
    class_ids : list[str]
        Ordered list of all class IDs.
    """
    student_ids = [s["id"] for s in students]
    class_ids = [c["id"] for c in classes]

    model.S = Set(initialize=student_ids)
    model.C = Set(initialize=class_ids)

    model.priority = Param(model.S, initialize={s["id"]: s.get("priority", 1) for s in students})

    def calc_focus_bonus(student_id: str, class_id: str) -> int:
        """
        Return the subject-focus preference bonus for a student-class pair.

        Parameters
        ----------
        student_id : str
            The student's unique identifier.
        class_id : str
            The class's unique identifier.

        Returns
        -------
        int
            Bonus value based on the student's preference rank for the class
            subject focus; 0 if there is no matching preference.
        """
        student_prefs = student_data[student_id].get("preferences", [])
        class_focus = class_data[class_id].get("subject_focus")
        if class_focus and class_focus in student_prefs:
            rank = student_prefs.index(class_focus)
            return len(student_prefs) - rank  # e.g., 3 prefs: 1st=3, 2nd=2, 3rd=1
        return 0

    focus_bonus = {(s, c): calc_focus_bonus(s, c) for s in student_ids for c in class_ids}
    model.focus_bonus = Param(model.S, model.C, initialize=focus_bonus)

    eligible_extended_day = [
        s
        for s in student_ids
        if student_data[s].get("extended_day_request")
        and student_data[s].get("extended_day_request") <= options.extended_day_time
    ]
    model.E = Set(initialize=eligible_extended_day)

    extended_day_penalty: dict[str, float] = {}
    extended_day_bonus: dict[str, float] = {}
    for s in student_ids:
        requested_time = student_data[s].get("extended_day_request")
        if s in eligible_extended_day:
            hours_past = requested_time - STANDARD_END_TIME
            student_priority = student_data[s].get("priority", 1)
            extended_day_penalty[s] = options.extended_day_penalty * hours_past
            extended_day_bonus[s] = options.extended_day_bonus * student_priority
        else:
            extended_day_penalty[s] = 0
            extended_day_bonus[s] = 0
    model.extended_day_penalty = Param(model.S, initialize=extended_day_penalty)
    model.extended_day_bonus = Param(model.S, initialize=extended_day_bonus)

    model.capacity = Param(model.C, initialize={c["id"]: c.get("capacity", 30) for c in classes})

    model.x = Var(model.S, model.C, domain=Binary)
    model.y = Var(model.E, domain=Binary)

    return eligible_extended_day, class_ids


def _add_objective(model: ConcreteModel) -> None:
    """
    Add the maximization objective to the model.

    The objective maximises the sum of student priority scores, subject-focus
    preference bonuses, and extended-day bonuses, minus extended-day penalties.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo concrete model to mutate. Must already have the sets,
        parameters, and variables populated by ``_build_sets_and_params``.
    """

    def objective_rule(m: ConcreteModel) -> Any:
        priority_score = sum(m.priority[s] * m.x[s, c] for s in m.S for c in m.C)
        focus_score = sum(m.focus_bonus[s, c] * m.x[s, c] for s in m.S for c in m.C)
        ext_bonus = sum(m.extended_day_bonus[s] * m.y[s] for s in m.E)
        ext_penalty = sum(m.extended_day_penalty[s] * m.y[s] for s in m.E)
        return priority_score + focus_score + ext_bonus - ext_penalty

    model.obj = Objective(rule=objective_rule, sense=maximize)


def _add_constraints(
    model: ConcreteModel,
    input_data: dict[str, Any],
    student_data: dict[str, dict[str, Any]],
    class_data: dict[str, dict[str, Any]],
    class_ids: list[str],
) -> None:
    """
    Add all constraints to the model.

    Adds the following constraints:

    * **one_class_per_student** — each student is assigned to at most one class.
    * **class_capacity** — total students in a class cannot exceed its capacity.
    * **no_same_class** — separated student pairs cannot share a class.
    * **class_level_match** — students may only be assigned to classes whose
      level matches their own.
    * **extended_day_requires_assignment** — extended day can only be granted
      when the student has a class assignment.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo concrete model to mutate.
    input_data : dict[str, Any]
        Raw problem input; used to read the ``"separations"`` list.
    student_data : dict[str, dict[str, Any]]
        Student records keyed by student ID.
    class_data : dict[str, dict[str, Any]]
        Class records keyed by class ID.
    class_ids : list[str]
        Ordered list of all class IDs.
    """

    def one_class_per_student_rule(m: ConcreteModel, s: str) -> Any:
        return sum(m.x[s, c] for c in m.C) <= 1

    model.one_class_per_student = Constraint(model.S, rule=one_class_per_student_rule)

    def class_capacity_rule(m: ConcreteModel, c: str) -> Any:
        return sum(m.x[s, c] for s in m.S) <= m.capacity[c]

    model.class_capacity = Constraint(model.C, rule=class_capacity_rule)

    separations = input_data.get("separations", [])
    separation_pairs = [
        (pair[0], pair[1])
        for pair in separations
        if len(pair) == 2 and pair[0] in student_data and pair[1] in student_data
    ]

    def no_same_class_rule(m: ConcreteModel, s1: str, s2: str, c: str) -> Any:
        return m.x[s1, c] + m.x[s2, c] <= 1

    model.no_same_class = Constraint(
        [(s1, s2, c) for (s1, s2) in separation_pairs for c in class_ids],
        rule=lambda m, s1, s2, c: no_same_class_rule(m, s1, s2, c),
    )

    def class_level_match_rule(m: ConcreteModel, s: str, c: str) -> Any:
        student_level = student_data[s].get("class_level")
        class_level = class_data[c].get("level")
        if student_level and class_level and student_level != class_level:
            return m.x[s, c] == 0
        return Constraint.Skip

    model.class_level_match = Constraint(model.S, model.C, rule=class_level_match_rule)

    def extended_day_requires_assignment_rule(m: ConcreteModel, s: str) -> Any:
        return m.y[s] <= sum(m.x[s, c] for c in m.C)

    model.extended_day_requires_assignment = Constraint(model.E, rule=extended_day_requires_assignment_rule)


def _extract_solution(
    model: ConcreteModel,
    student_data: dict[str, dict[str, Any]],
    class_data: dict[str, dict[str, Any]],
    eligible_extended_day: list[str],
    students: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Extract assignments and unassigned students from the solved model.

    Iterates over the student set and reads the binary assignment variable
    ``x`` to determine which class (if any) each student was assigned to.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo model after ``solver.solve()`` has been called.
    student_data : dict[str, dict[str, Any]]
        Student records keyed by student ID.
    class_data : dict[str, dict[str, Any]]
        Class records keyed by class ID.
    eligible_extended_day : list[str]
        Student IDs that were eligible for an extended-day grant.
    students : list[dict[str, Any]]
        Original list of student records (used for total count).

    Returns
    -------
    dict[str, Any]
        A dict with keys:

        * ``assignments`` — list of dicts describing each successful assignment.
        * ``unassigned`` — list of dicts for students with no class assigned.
        * ``total_assigned`` — count of assigned students.
        * ``total_students`` — total number of students in the input.
    """
    assignments: list[dict[str, Any]] = []
    unassigned: list[dict[str, Any]] = []

    for s in model.S:
        assigned = False
        for c in model.C:
            if value(model.x[s, c]) > 0.5:
                student_prefs = student_data[s].get("preferences", [])
                class_focus = class_data[c].get("subject_focus")
                pref_match = class_focus in student_prefs if student_prefs and class_focus else None
                requested_extended_day = student_data[s].get("extended_day_request")
                extended_day_granted = s in eligible_extended_day and value(model.y[s]) > 0.5
                assignments.append(
                    {
                        "student_id": s,
                        "class_id": c,
                        "student_name": student_data[s].get("name", s),
                        "class_name": class_data[c].get("name", c),
                        "subject_focus": class_focus,
                        "focus_preference_match": pref_match,
                        "extended_day_requested": requested_extended_day,
                        "extended_day_granted": extended_day_granted,
                    }
                )
                assigned = True
                break
        if not assigned:
            unassigned.append(
                {
                    "student_id": s,
                    "student_name": student_data[s].get("name", s),
                    "reason": "No suitable class available",
                }
            )

    return {
        "assignments": assignments,
        "unassigned": unassigned,
        "total_assigned": len(assignments),
        "total_students": len(students),
    }


def _compute_metrics(
    model: ConcreteModel,
    solution: dict[str, Any],
    results: Any,
    student_data: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute summary metrics from the solution.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo model after solving; used to read the objective value.
    solution : dict[str, Any]
        The solution dict returned by ``_extract_solution``.
    results : Any
        The solver results object returned by ``solver.solve()``.
    student_data : dict[str, dict[str, Any]]
        Student records keyed by student ID; used to check preference lists.

    Returns
    -------
    dict[str, Any]
        A dict with keys:

        * ``value`` — objective value of the solution.
        * ``assigned_students`` — number of students assigned to a class.
        * ``unassigned_students`` — number of students not assigned.
        * ``preferences_met`` — count of assignments matching the student's
          top-ranked subject preference.
        * ``preferences_met_percentage`` — percentage of students-with-prefs
          whose preference was met, rounded to one decimal place.
        * ``extended_day_requests`` — count of assigned students who requested
          extended day.
        * ``extended_day_granted`` — count of students whose extended-day
          request was approved by the solver.
        * ``extended_day_granted_percentage`` — approval rate as a percentage,
          rounded to one decimal place.
        * ``solver_status`` — string representation of the solver status.
        * ``termination_condition`` — string representation of the termination
          condition.
    """
    assignments = solution["assignments"]

    students_with_prefs = [a for a in assignments if student_data[a["student_id"]].get("preferences")]
    prefs_met = sum(1 for a in assignments if a.get("focus_preference_match") is True)
    pref_percentage = (prefs_met / len(students_with_prefs) * 100) if students_with_prefs else 0

    extended_day_requests = sum(1 for a in assignments if a.get("extended_day_requested") is not None)
    extended_day_granted_count = sum(1 for a in assignments if a.get("extended_day_granted") is True)
    extended_day_percentage = (extended_day_granted_count / extended_day_requests * 100) if extended_day_requests else 0

    return {
        "value": value(model.obj) if value(model.obj) else 0,
        "assigned_students": solution["total_assigned"],
        "unassigned_students": len(solution["unassigned"]),
        "preferences_met": prefs_met,
        "preferences_met_percentage": round(pref_percentage, 1),
        "extended_day_requests": extended_day_requests,
        "extended_day_granted": extended_day_granted_count,
        "extended_day_granted_percentage": round(extended_day_percentage, 1),
        "solver_status": str(results.solver.status),
        "termination_condition": str(results.solver.termination_condition),
    }


if __name__ == "__main__":
    main()
