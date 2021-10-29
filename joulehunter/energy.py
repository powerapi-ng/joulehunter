# Allows the use of standard collection type hinting from Python 3.7 onwards
from __future__ import annotations

from collections.abc import Generator
import os
from typing import Any

RAPL_API_DIR = "/sys/devices/virtual/powercap/intel-rapl"


def available_domains() -> list[dict[str, Any]]:
    if not os.path.exists(RAPL_API_DIR):
        raise RuntimeError("RAPL API is not available on this machine")

    packages = [
        {"dirname": dirname,
         "name": domain_name([dirname]),
         "components": []}
        for dirname in sorted(os.listdir(RAPL_API_DIR))
        if dirname.startswith("intel-rapl")]

    for package in packages:
        package["components"] = [
            {"dirname": dirname,
             "name": domain_name([package["dirname"], dirname])}
            for dirname
            in sorted(os.listdir(os.path.join(RAPL_API_DIR,
                                              package["dirname"])))
            if dirname.startswith("intel-rapl")]

    return packages


def domain_name(dirnames: list[str]) -> str:
    rapl_name_path = os.path.join(RAPL_API_DIR, *dirnames, "name")
    if not os.path.exists(rapl_name_path):
        raise RuntimeError("Domain not found")
    with open(rapl_name_path, "r") as file:
        return file.readline().strip()


def stringify_domains(domains: list[dict[str, Any]]) -> str:
    text = ""
    for package_num, package in enumerate(domains):
        text += f"[{package_num}] {package['name']}\n"
        for component_num, component in enumerate(package["components"]):
            text += f"  [{component_num}] {component['name']}\n"
    text = text[:-1]
    return text


def package_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for package in domains:
        if package['name'] == name:
            return package['dirname'].split(':')[-1]
    raise RuntimeError("Package name not found")


def component_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for package in domains:
        for component in package["components"]:
            if component['name'] == name:
                return component['dirname'].split(':')[-1]
    raise RuntimeError("Component name not found")


def dirnames_to_names(domains: list[dict[str, Any]],
                      dirnames: list[str]) -> list[str]:
    names = []
    for dirname in dirnames:
        for package in domains:
            if package['dirname'] == dirname:
                names.append(package['name'])
            for component in package["components"]:
                if component['dirname'] == dirname:
                    names.append(component['name'])
    return names


def parse_domain(package, component):
    available_domains_ = available_domains()

    package = str(package)
    if not package.isnumeric():
        package = package_name_to_num(available_domains_, package)

    domain = [f'intel-rapl:{package}']

    if component is not None:
        component = str(component)
        if not component.isnumeric():
            component = component_name_to_num(available_domains_, component)
        domain.append(f'intel-rapl:{package}:{component}')

    return domain


class Energy:
    def __init__(self, dirnames: list[str]) -> None:
        self.generator = Energy.current_energy_generator(dirnames)

    @staticmethod
    def current_energy_generator(dirnames: list[str]) -> Generator[
            float, None, None]:
        rapl_energy_path = os.path.join(RAPL_API_DIR, *dirnames, 'energy_uj')

        if not os.path.exists(rapl_energy_path):
            raise RuntimeError("Domain not found")
        with open(rapl_energy_path, 'r') as file:
            while True:
                energy = float(file.readline()[:-1]) / 10**6
                file.seek(0)
                yield energy

    def current_energy(self) -> float:
        return next(self.generator)
