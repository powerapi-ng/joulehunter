import distutils
import os
import subprocess
import sys
from setuptools import Extension, find_packages, setup

setup(
    name="joulehunter",
    packages=find_packages(),
    ext_modules=[
        Extension(
            "joulehunter.low_level.stat_profile",
            sources=["joulehunter/low_level/stat_profile.c"],
        )
    ],
    keywords=["profiling", "profile", "profiler",
              "energy", "cpu", "time", "sampling"],
    install_requires=[],
    include_package_data=True,
    python_requires=">=3.7",
    entry_points={"console_scripts": [
        "joulehunter = joulehunter.__main__:main"]},
    zip_safe=False,

)
