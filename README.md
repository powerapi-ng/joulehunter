joulehunter 
=========== 
[![Unit tests](https://github.com/powerapi-ng/joulehunter/actions/workflows/test.yaml/badge.svg)](https://github.com/powerapi-ng/joulehunter/actions/workflows/test.yaml)
[![PyPI version](https://badge.fury.io/py/joulehunter.svg)](https://badge.fury.io/py/joulehunter)
![screenshot](https://user-images.githubusercontent.com/11022568/134655797-3872379e-0e4e-48d6-a771-6a94c756fa67.png)

Joulehunter helps you find what part of your code is consuming considerable amounts of energy .

This repo is still a work in progress. 😄

Compatibility
------------

Joulehunter runs on **Linux** machines with **Intel RAPL** support. This technology has been available since the Sandy Bridge generation.


Installation
------------

    pip install joulehunter 

Usage
------------

Joulehunter works similarly to [pyinstrument](https://github.com/joerick/pyinstrument), as we forked the repo and replaced time measuring with energy measuring. Here's [pyinstrument's documentation](https://pyinstrument.readthedocs.io/).

```joulehunter -l``` will list the available domains on this machine. These include the packages and their components, such as the DRAM and core.

The command ```joulehunter main.py``` will execute ```main.py``` and measure the energy consumption of the first package (CPU).

To select the package to analyze use the option ```-p``` or ```--package``` followed by the package number or the package name. The default value is 0.

The options ```-c``` and ```--component``` allow you to measure the energy of an individual component by specifying their name or ID. If not specified, the entire package will be selected.


### Example

Executing ```joulehunter -l``` could output this:
    
    [0] package-0
      [0] core
      [1] uncore
      [2] dram
    [1] package-1
      [0] core
      [1] uncore
      [2] dram

If we run ```joulehunter -p package-1 -c 2 my_file.py```, joulehunter will execute ```my_file.py``` and measure the energy consumption of package-1's DRAM.

Requirements 
-------------
Sometimes when installing **joulehunter** pip can't build the .c modules, therefore you will have to install **python3-devel** to enable gcc to compile the .c modules 

Read permission
---------------

Due to a [security vulnerability](https://platypusattack.com), only root has read permission for the energy files. In order to circumvent this, run the script as root or grant read permissions for the following files:

    /sys/devices/virtual/powercap/intel-rapl/intel-rapl:*/energy_uj
    /sys/devices/virtual/powercap/intel-rapl/intel-rapl:*/intel-rapl:*:*/energy_uj
    
More info [here](https://github.com/powerapi-ng/pyJoules/issues/13).

Acknowledgments
------------

Thanks to [Joe Rickerby](https://github.com/joerick) and all of [pyinstrument](https://github.com/joerick/pyinstrument)'s contributors.

This fork is being developed by [Chakib Belgaid](https://github.com/chakib-belgaid) and [Alex Kaminetzky](https://github.com/akaminetzkyp). Feel free to ask us any questions!
