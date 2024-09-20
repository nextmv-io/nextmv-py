import gurobipy as gp


class GurobipySolution:
    """Gurobipy solution representation."""

    def __init__(self, model: gp.Model):
        self._model = model

    @classmethod
    def from_model(cls, model: gp.Model):
        return cls(model)

    def to_dict(self):
        if self._model.SolCount < 1:
            return None

        return {x.VarName: x.X for x in self._model.getVars()}
