"""Nextmv & Gurobi Python SDK."""

from .__about__ import __version__
from .model import Model as Model
from .options import OPTION_TYPE_TRANSLATION as OPTION_TYPE_TRANSLATION
from .options import SKIP_PARAMETERS as SKIP_PARAMETERS
from .options import ModelOptions as ModelOptions
from .solution import ModelSolution as ModelSolution
from .statistics import STATUS as STATUS
from .statistics import ModelStatistics as ModelStatistics

VERSION = __version__
"""The version of the Nextmv & Gurobi Python SDK."""
