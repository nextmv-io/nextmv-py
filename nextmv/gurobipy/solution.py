import gurobipy as gp
from pydantic import ConfigDict

from nextmv.base_model import BaseModel


class GurobipySolution(BaseModel):
    """Gurobipy solution representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: gp.Model = None

    @classmethod
    def from_model(cls, model: gp.Model):
        return cls(model=model)

    def to_dict(self):
        if self.model.SolCount < 1:
            return None

        return {x.VarName: x.X for x in self.model.getVars()}
