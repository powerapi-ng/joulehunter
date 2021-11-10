from __future__ import annotations

import codecs
import os
import tempfile
import urllib.parse
import webbrowser
from typing import Any

from joulehunter import processors
from joulehunter.renderers.base import ProcessorList, Renderer
from joulehunter.renderers.jsonrenderer import JSONRenderer
from joulehunter.session import Session

# pyright: strict


class HTMLRenderer(Renderer):
    """
    Renders a rich, interactive web page, as a string of HTML.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def render(self, session: Session):
        session_json = self.render_json(session)

        page = """<!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/spiermar/d3-flame-graph@2.0.3/dist/d3-flamegraph.css">

            <style>

            /* Space out content a bit */
            body {
              padding-top: 20px;
              padding-bottom: 20px;
            }

            /* Custom page header */
            .header {
              padding-bottom: 20px;
              padding-right: 15px;
              padding-left: 15px;
              border-bottom: 1px solid #e5e5e5;
            }

            /* Make the masthead heading the same height as the navigation */
            .header h3 {
              margin-top: 0;
              margin-bottom: 0;
              line-height: 40px;
            }

            /* Customize container */
            .container {
              max-width: 990px;
            }
            </style>

            <title>d3-flame-graph energy</title>

            <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
            <!--[if lt IE 9]>
              <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
              <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
            <![endif]-->
          </head>
          <body>
            <div class="container">
              <div class="header clearfix">
                <nav>
                  <div class="pull-right">
                    <form class="form-inline" id="form">
                      <a class="btn" href="javascript: resetZoom();">Reset zoom</a>
                      <a class="btn" href="javascript: clear();">Clear</a>
                      <div class="form-group">
                        <input type="text" class="form-control" id="term">
                      </div>
                      <a class="btn btn-primary" href="javascript: search();">Search</a>
                    </form>
                  </div>
                </nav>
                <h3 class="text-muted">d3-flame-graph energy</h3>
              </div>
              <div id="chart">
              </div>
              <hr>
              <div id="details">
              </div>
            </div>

            <!-- D3.js -->
            <script src="https://d3js.org/d3.v4.min.js" charset="utf-8"></script>

            <!-- d3-tip -->
            <script type="text/javascript" src=https://cdnjs.cloudflare.com/ajax/libs/d3-tip/0.9.1/d3-tip.min.js></script>

            <!-- d3-flamegraph -->
            <script type="text/javascript" src="https://cdn.jsdelivr.net/gh/spiermar/d3-flame-graph@2.0.3/dist/d3-flamegraph.min.js"></script>

            <script type="text/javascript">
            var flameGraph = d3.flamegraph()
              .width(960)
              .cellHeight(18)
              .transitionDuration(750)
              .minFrameSize(5)
              .transitionEase(d3.easeCubic)
              .sort(true)
              //Example to sort in reverse order
              //.sort(function(a,b){ return d3.descending(a.name, b.name);})
              .title("")
              .onClick(onClick)
              .differential(false)
              .selfValue(false);


            // Example on how to use custom tooltips using d3-tip.
            // var tip = d3.tip()
            //   .direction("s")
            //   .offset([8, 0])
            //   .attr('class', 'd3-flame-graph-tip')
            //   .html(function(d) { return "name: " + d.data.name + ", value: " + d.data.value; });

            // flameGraph.tooltip(tip);

            var details = document.getElementById("details");
            flameGraph.setDetailsElement(details);

            // Example on how to use custom labels
            // var label = function(d) {
            //  return "name: " + d.name + ", value: " + d.value;
            // }
            // flameGraph.label(label);

            // Example of how to set fixed chart height
            // flameGraph.height(540);

              var data = """ + session_json + """
              d3.select("#chart")
                  .datum(data)
                  .call(flameGraph);

            document.getElementById("form").addEventListener("submit", function(event){
              event.preventDefault();
              search();
            });

            function search() {
              var term = document.getElementById("term").value;
              flameGraph.search(term);
            }

            function clear() {
              document.getElementById('term').value = '';
              flameGraph.clear();
            }

            function resetZoom() {
              flameGraph.resetZoom();
            }

            function onClick(d) {
              console.info("Clicked on " + d.data.name);
            }
            </script>
          </body>
        </html>"""

        return page

    def open_in_browser(self, session: Session, output_filename: str | None = None):
        """
        Open the rendered HTML in a webbrowser.

        If output_filename=None (the default), a tempfile is used.

        The filename of the HTML file is returned.

        """
        if output_filename is None:
            output_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            output_filename = output_file.name
            with codecs.getwriter("utf-8")(output_file) as f:
                f.write(self.render(session))
        else:
            with codecs.open(output_filename, "w", "utf-8") as f:
                f.write(self.render(session))

        url = urllib.parse.urlunparse(("file", "", output_filename, "", "", ""))
        webbrowser.open(url)
        return output_filename

    def render_json(self, session: Session):
        json_renderer = JSONRenderer()
        json_renderer.processors = self.processors
        json_renderer.processor_options = self.processor_options
        return json_renderer.render(session)

    def default_processors(self) -> ProcessorList:
        return [
            processors.remove_importlib,
            processors.merge_consecutive_self_time,
            processors.aggregate_repeated_calls,
            processors.group_library_frames_processor,
            processors.remove_unnecessary_self_time_nodes,
            processors.remove_irrelevant_nodes,
        ]
