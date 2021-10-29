from typing import Any
import joulehunter
from joulehunter import processors
from joulehunter.frame import BaseFrame
from joulehunter.renderers.base import ProcessorList, Renderer
from joulehunter.session import Session
from joulehunter.util import truncate

# pyright: strict


class ConsoleRenderer(Renderer):
    """
    Produces text-based output, suitable for text files or ANSI-compatible
    consoles.
    """

    def __init__(self, unicode: bool = False, color: bool = False, **kwargs: Any):
        """
        :param unicode: Use unicode, like box-drawing characters in the output.
        :param color: Enable color support, using ANSI color sequences.
        """
        super().__init__(**kwargs)

        self.unicode = unicode
        self.color = color
        self.colors = self.colors_enabled if color else self.colors_disabled

    def render(self, session: Session):
        result = self.render_preamble(session)

        frame = self.preprocess(session.root_frame())

        if frame is None:
            result += "No samples were recorded.\n\n"
            return result

        self.root_frame = frame
        result += self.render_frame(
            self.root_frame, total_energy=self.root_frame.time())
        result += "\n"

        return result

    # pylint: disable=W1401
    def render_preamble(self, session: Session):
        c = self.colors
        lines = [
            "",
            f"{c.bold}{c.cyan}   . _     / _  /_    _ _/_ _  _  {c.end}{c.end}",
            f"{c.bold}{c.cyan}  / /_//_// /_'/ //_// //  /_'/   {c.end}{c.end}",
            f"{c.bold}{c.cyan}|/                                {c.end}{c.end}",
        ]
        lines[1] += f"{c.cyan}Duration:{c.end} {session.duration:<12.3f}"
        lines[2] += f"{c.cyan}Package:{c.end}  {session.domain_names[0]:<12}"
        lines[3] += f"{c.cyan}Program:{c.end}  {session.program}"

        lines[1] += f"{c.cyan}Samples:{c.end}   {session.sample_count}"
        if len(session.domain_names) == 2:
            lines[2] += f"{c.cyan}Component:{c.end} {session.domain_names[1]}"
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def render_frame(
            self, frame: BaseFrame,
            indent: str = "",
            child_indent: str = "",
            total_energy: float = None) -> str:
        if not frame.group or (
            frame.group.root == frame
            or frame.total_self_time > 0.2 * self.root_frame.time()
            or frame in frame.group.exit_frames
        ):
            time_str = (self._ansi_color_for_time(frame)
                        + f"{frame.time():.3f} J")
            if total_energy:
                percentage = frame.time() / total_energy * 100
                time_str += f" [{percentage:.1f}%]"
            time_str += self.colors.end
            function_color = self._ansi_color_for_function(frame)
            result = "{indent}{time_str} {function_color}{function}{c.end}  {c.faint}{code_position}{c.end}\n".format(
                indent=indent,
                time_str=time_str,
                function_color=function_color,
                function=frame.function,
                code_position=frame.code_position_short,
                c=self.colors,
            )
            if self.unicode:
                indents = {"├": "├─ ", "│": "│  ", "└": "└─ ", " ": "   "}
            else:
                indents = {"├": "|- ", "│": "|  ", "└": "`- ", " ": "   "}

            if frame.group and frame.group.root == frame:
                result += "{indent}[{count} frames hidden]  {c.faint}{libraries}{c.end}\n".format(
                    indent=child_indent + "   ",
                    count=len(frame.group.frames),
                    libraries=truncate(", ".join(frame.group.libraries), 40),
                    c=self.colors,
                )
                for key in indents:
                    indents[key] = "      "
        else:
            result = ""
            indents = {"├": "", "│": "", "└": "", " ": ""}

        if frame.children:
            last_child = frame.children[-1]

            for child in frame.children:
                if child is not last_child:
                    c_indent = child_indent + indents["├"]
                    cc_indent = child_indent + indents["│"]
                else:
                    c_indent = child_indent + indents["└"]
                    cc_indent = child_indent + indents[" "]
                result += self.render_frame(
                    child, indent=c_indent, child_indent=cc_indent,
                    total_energy=total_energy)

        return result

    def _ansi_color_for_time(self, frame: BaseFrame):
        proportion_of_total = frame.time() / self.root_frame.time()

        if proportion_of_total > 0.6:
            return self.colors.red
        elif proportion_of_total > 0.2:
            return self.colors.yellow
        elif proportion_of_total > 0.05:
            return self.colors.green
        else:
            return self.colors.bright_green + self.colors.faint

    def _ansi_color_for_function(self, frame: BaseFrame):
        if frame.is_application_code:
            return self.colors.bg_dark_blue_255 + self.colors.white_255
        else:
            return ""

    def default_processors(self) -> ProcessorList:
        return [
            processors.remove_importlib,
            processors.merge_consecutive_self_time,
            processors.aggregate_repeated_calls,
            processors.group_library_frames_processor,
            processors.remove_unnecessary_self_time_nodes,
            processors.remove_irrelevant_nodes,
        ]

    class colors_enabled:
        red = "\033[31m"
        green = "\033[32m"
        yellow = "\033[33m"
        blue = "\033[34m"
        cyan = "\033[36m"
        bright_green = "\033[92m"
        white = "\033[37m\033[97m"

        bg_dark_blue_255 = "\033[48;5;24m"
        white_255 = "\033[38;5;15m"

        bold = "\033[1m"
        faint = "\033[2m"

        end = "\033[0m"

    class colors_disabled:
        red = ""
        green = ""
        yellow = ""
        blue = ""
        cyan = ""
        bright_green = ""
        white = ""

        bg_dark_blue_255 = ""
        white_255 = ""

        bold = ""
        faint = ""

        end = ""
