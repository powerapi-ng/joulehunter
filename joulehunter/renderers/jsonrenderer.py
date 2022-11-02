from __future__ import annotations

import json
from typing import Any, Callable

from joulehunter import processors
from joulehunter.frame import BaseFrame
from joulehunter.renderers.base import ProcessorList, Renderer
from joulehunter.session import Session

# pyright: strict


# note: this file is called jsonrenderer to avoid hiding built-in module 'json'.

encode_str: Callable[[str], str] = json.encoder.encode_basestring  # type: ignore


def encode_bool(a_bool: bool):
    return "true" if a_bool else "false"


class JSONRenderer(Renderer):
    """
    Outputs a tree of JSON, containing processed frames.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def render_frame(self, frame: BaseFrame | None):
        if frame is None:
            return "null"
        # we don't use the json module because it uses 2x stack frames, so
        # crashes on deep but valid call stacks

        property_decls: list[str] = []
        property_decls.append('"function": %s' % encode_str(frame.function or ""))
        property_decls.append('"file_path_short": %s' % encode_str(frame.file_path_short or ""))
        property_decls.append('"file_path": %s' % encode_str(frame.file_path or ""))
        property_decls.append('"line_no": %d' % frame.line_no)
        property_decls.append('"time": %f' % frame.time())
        property_decls.append('"await_time": %f' % frame.await_time())
        property_decls.append(
            '"is_application_code": %s' % encode_bool(frame.is_application_code or False)
        )

        # can't use list comprehension here because it uses two stack frames each time.
        children_jsons: list[str] = []
        for child in frame.children:
            children_jsons.append(self.render_frame(child))
        property_decls.append('"children": [%s]' % ",".join(children_jsons))

        if frame.group:
            property_decls.append('"group_id": %s' % encode_str(frame.group.id))

        return "{%s}" % ",".join(property_decls)

    def render(self, session: Session):
        frame = self.preprocess(session.root_frame())

        property_decls: list[str] = []
        property_decls.append('"start_time": %f' % session.start_time)
        property_decls.append('"duration": %f' % session.duration)
        property_decls.append('"sample_count": %d' % session.sample_count)
        property_decls.append('"program": %s' % encode_str(session.program))
        property_decls.append(
            '"package": %s' % encode_str(session.domain_names[0]))
        if len(session.domain_names) == 2:
            property_decls.append(
                '"component": %s' % encode_str(session.domain_names[1]))
        else:
            property_decls.append('"component": null')
        property_decls.append('"root_frame": %s' % self.render_frame(frame))

        return "{%s}\n" % ",".join(property_decls)

    def default_processors(self) -> ProcessorList:
        return [
            processors.remove_importlib,
            processors.merge_consecutive_self_time,
            processors.aggregate_repeated_calls,
            processors.group_library_frames_processor,
            processors.remove_unnecessary_self_time_nodes,
            processors.remove_irrelevant_nodes,
        ]
