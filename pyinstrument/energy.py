# Allows the use of standard collection type hinting from Python 3.7 onwards
from __future__ import annotations

import os
from typing import Any

RAPL_API_DIR = '/sys/devices/virtual/powercap/intel-rapl'


def available_domains() -> list[dict[str, Any]]:
    if not os.path.exists(RAPL_API_DIR):
        raise RuntimeError('RAPL API is not available on this machine')

    sockets = [
        {'dirname': dirname,
         'name': domain_name([dirname]),
         'scopes': []}
        for dirname in sorted(os.listdir(RAPL_API_DIR))
        if dirname.startswith('intel-rapl')]

    for socket in sockets:
        socket['scopes'] = [
            {'dirname': dirname,
             'name': domain_name([socket['dirname'], dirname])}
            for dirname
            in sorted(os.listdir(os.path.join(RAPL_API_DIR, socket['dirname'])))
            if dirname.startswith('intel-rapl')]

    return sockets


def domain_name(dirnames: list[str]) -> str:
    with open(os.path.join(RAPL_API_DIR, *dirnames, 'name'), 'r') as file:
        return file.readline().strip()


def stringify_domains(domains: list[dict[str, Any]]) -> str:
    text = ''
    for socket_num, socket in enumerate(domains):
        text += f'[{socket_num}] {socket["name"]}\n'
        for scope_num, scope in enumerate(socket['scopes']):
            text += f'  [{scope_num}] {scope["name"]}\n'
    text = text[:-1]
    return text
