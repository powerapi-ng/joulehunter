# Allows the use of standard collection type hinting from Python 3.7 onwards
from __future__ import annotations

from collections.abc import Generator
import os
from typing import Any

RAPL_API_DIR = "/sys/devices/virtual/powercap/intel-rapl"


def available_domains() -> list[dict[str, Any]]:
    if not os.path.exists(RAPL_API_DIR):
        raise RuntimeError("RAPL API is not available on this machine")

    sockets = [
        {"dirname": dirname,
         "name": domain_name([dirname]),
         "scopes": []}
        for dirname in sorted(os.listdir(RAPL_API_DIR))
        if dirname.startswith("intel-rapl")]

    for socket in sockets:
        socket["scopes"] = [
            {"dirname": dirname,
             "name": domain_name([socket["dirname"], dirname])}
            for dirname
            in sorted(os.listdir(os.path.join(RAPL_API_DIR, socket["dirname"])))
            if dirname.startswith("intel-rapl")]

    return sockets


def domain_name(dirnames: list[str]) -> str:
    with open(os.path.join(RAPL_API_DIR, *dirnames, "name"), "r") as file:
        return file.readline().strip()


def stringify_domains(domains: list[dict[str, Any]]) -> str:
    text = ""
    for socket_num, socket in enumerate(domains):
        text += f"[{socket_num}] {socket['name']}\n"
        for scope_num, scope in enumerate(socket["scopes"]):
            text += f"  [{scope_num}] {scope['name']}\n"
    text = text[:-1]
    return text


def package_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for socket in domains:
        if socket['name'] == name:
            return socket['dirname'].split(':')[-1]
    raise RuntimeError("Package not found")


def scope_name_to_num(domains: list[dict[str, Any]], name: str) -> str:
    for socket in domains:
        for scope in socket["scopes"]:
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
    def __init__(self, domains):
        self.domains = domains
        self.generator = Energy.current_energy_generator(domains)

    @staticmethod
    def current_energy_generator(domains: list[str]) -> Generator[
            float, None, None]:
        rapl_api_path = os.path.join(RAPL_API_DIR, *domains, 'energy_uj')

        if not os.path.exists(rapl_api_path):
            raise RuntimeError("Domain not found")
        with open(rapl_api_path, 'r') as file:
            while True:
                energy = float(file.readline()[:-1]) / 10 ** 6
                file.seek(0)
                yield energy

    def current_energy(self) -> float:
        return next(self.generator)
