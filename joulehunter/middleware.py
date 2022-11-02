import io
import os
import sys
import time

from django.conf import settings
from django.http import HttpResponse
from django.utils.module_loading import import_string

from joulehunter import Profiler
from joulehunter.renderers.html import HTMLRenderer

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class ProfilerMiddleware(MiddlewareMixin):  # type: ignore
    def process_request(self, request):
        profile_dir = getattr(settings, "JOULEHUNTER_PROFILE_DIR", None)

        func_or_path = getattr(settings, "JOULEHUNTER_SHOW_CALLBACK", None)
        if isinstance(func_or_path, str):
            show_joulehunter = import_string(func_or_path)
        elif callable(func_or_path):
            show_joulehunter = func_or_path
        else:
            show_joulehunter = lambda request: True

        if (
            show_joulehunter(request)
            and getattr(settings, "JOULEHUNTER_URL_ARGUMENT", "profile") in request.GET
        ) or profile_dir:
            package = request.GET.get(
                "package",
                getattr(settings, "JOULEHUNTER_PACKAGE", None)
            )
            component = request.GET.get(
                "component",
                getattr(settings, "JOULEHUNTER_COMPONENT", None)
            )
            if package == '':
                package = None
            if component == '':
                component = None

            if package is not None:
                profiler = Profiler(package=package,
                                    component=component)
            else:
                profiler = Profiler(component=component)
            profiler.start()

            request.profiler = profiler

    def process_response(self, request, response):
        if hasattr(request, "profiler"):
            profile_session = request.profiler.stop()

            renderer = HTMLRenderer()
            output_html = renderer.render(profile_session)

            profile_dir = getattr(settings, "JOULEHUNTER_PROFILE_DIR", None)

            # Limit the length of the file name (255 characters is the max limit on major current OS, but it is rather
            # high and the other parts (see line 36) are to be taken into account; so a hundred will be fine here).
            path = request.get_full_path().replace("/", "_")[:100]

            # Swap ? for _qs_ on Windows, as it does not support ? in filenames.
            if sys.platform in ["win32", "cygwin"]:
                path = path.replace("?", "_qs_")

            if profile_dir:
                filename = "{total_time:.3f}s {path} {timestamp:.0f}.html".format(
                    total_time=profile_session.duration,
                    path=path,
                    timestamp=time.time(),
                )

                file_path = os.path.join(profile_dir, filename)

                if not os.path.exists(profile_dir):
                    os.mkdir(profile_dir)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output_html)

            if getattr(settings, "JOULEHUNTER_URL_ARGUMENT", "profile") in request.GET:
                return HttpResponse(output_html)
            else:
                return response
        else:
            return response
