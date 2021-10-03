import warnings

from joulehunter.profiler import Profiler

__version__ = "1.0.0"

# enable deprecation warnings
warnings.filterwarnings("once", ".*", DeprecationWarning, r"joulehunter\..*")
