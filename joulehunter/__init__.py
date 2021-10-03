import warnings


__version__ = "4.0.3"

# enable deprecation warnings
warnings.filterwarnings("once", ".*", DeprecationWarning, r"joulehunter\..*")
