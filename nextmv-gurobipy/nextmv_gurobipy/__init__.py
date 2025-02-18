"""Nextmv & Gurobi Python SDK."""

from .__about__ import __version__
from .model import Model as Model
from .options import ModelOptions as ModelOptions
from .solution import ModelSolution as ModelSolution
from .statistics import Statistics as Statistics

VERSION = __version__
"""The version of the Nextmv & Gurobi Python SDK."""
