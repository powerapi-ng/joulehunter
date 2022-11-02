import warnings

from joulehunter.profiler import Profiler

__version__ = "v1.0.2"

# enable deprecation warnings
warnings.filterwarnings("once", ".*", DeprecationWarning, r"joulehunter\..*")
