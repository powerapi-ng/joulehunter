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
         "scopes": []}
        for dirname in sorted(os.listdir(RAPL_API_DIR))
        if dirname.startswith("intel-rapl")]

    for package in packages:
        package["scopes"] = [
            {"dirname": dirname,
             "name": domain_name([package["dirname"], dirname])}
            for dirname
            in sorted(os.listdir(os.path.join(RAPL_API_DIR,
                                              package["dirname"])))
            if dirname.startswith("intel-rapl")]

    return packages


def domain_name(dirnames: list[str]) -> str:
    with open(os.path.join(RAPL_API_DIR, *dirnames, "name"), "r") as file:
        return file.readline().strip()


def stringify_domains(domains: list[dict[str, Any]]) -> str:
    text = ""
    for package_num, package in enumerate(domains):
        text += f"[{package_num}] {package['name']}\n"
        for scope_num, scope in enumerate(package["scopes"]):
            text += f"  [{scope_num}] {scope['name']}\n"
    text = text[:-1]
    return text


def package_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for package in domains:
        if package['name'] == name:
            return package['dirname'].split(':')[-1]
    raise RuntimeError("Package not found")


def scope_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for package in domains:
        for scope in package["scopes"]:
            if scope['name'] == name:
                return scope['dirname'].split(':')[-1]
    raise RuntimeError("Scope not found")


def dirnames_to_names(domains: list[dict[str, Any]],
                      dirnames: list[str]) -> list[str]:
    names = []
    for dirname in dirnames:
        for package in domains:
            if package['dirname'] == dirname:
                names.append(package['name'])
            for scope in package["scopes"]:
                if scope['dirname'] == dirname:
                    names.append(scope['name'])
    return names


class Energy:
    def __init__(self, dirnames):
        self.generator = Energy.current_energy_generator(dirnames)

    @staticmethod
    def current_energy_generator(dirnames: list[str]) -> Generator[
            float, None, None]:
        rapl_api_path = os.path.join(RAPL_API_DIR, *dirnames, 'energy_uj')

        if not os.path.exists(rapl_api_path):
            raise RuntimeError("Domain not found")
        with open(rapl_api_path, 'r') as file:
            while True:
                energy = float(file.readline()[:-1]) / 10 ** 6
                file.seek(0)
                yield energy

    def current_energy(self) -> float:
        return next(self.generator)
