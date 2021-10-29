import sys

import pytest

from joulehunter import stack_sampler, Profiler
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(autouse=True)
def check_sampler_state():
    assert sys.getprofile() is None
    assert len(stack_sampler.get_stack_sampler().subscribers) == 0

    try:
        yield
        assert sys.getprofile() is None
        assert len(stack_sampler.get_stack_sampler().subscribers) == 0
    finally:
        sys.setprofile(None)
        stack_sampler.thread_locals.__dict__.clear()


def current_energy_generator():
    i = 0
    while True:
        i += 1
        yield i


def current_energy():
    return next(current_energy_generator.generator)


def new_init(self, async_mode="disabled"):
    self._interval = 0.001
    self._last_session = None
    self._active_session = None
    self._async_mode = async_mode
    self.current_energy = current_energy
    self.domain_names = ["0", "mockup"]


@pytest.fixture(autouse=True)
def mock_profiler():
    MonkeyPatch().setattr(Profiler, "__init__", new_init)
    myprofiler = Profiler()
    return myprofiler
