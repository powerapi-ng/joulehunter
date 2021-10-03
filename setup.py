import distutils
import os
import subprocess
import sys

from setuptools import Extension, find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

setup(
    name="joulehunter",
    packages=find_packages(),
    version="4.0.3",
    ext_modules=[
        Extension(
            "joulehunter.low_level.stat_profile",
            sources=["joulehunter/low_level/stat_profile.c"],
        )
    ],
    description="Call stack profiler for Python. Shows you why your code is slow!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="chakib belgaid",
    author_email="chakib.belgaid@gmail.com",
    url="https://github.com/powerapi-ng/joulehunter",
    keywords=["profiling", "profile", "profiler",
              "energy", "cpu", "time", "sampling"],
    install_requires=[],
    include_package_data=True,
    python_requires=">=3.7",
    entry_points={"console_scripts": [
        "joulehunter = joulehunter.__main__:main"]},
    zip_safe=False,
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Testing",
    ],
)
