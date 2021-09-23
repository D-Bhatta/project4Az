import logging
import os
import random
import socket
import sys
from datetime import datetime

import redis
from flask import Flask, render_template, request
from opencensus.ext.azure import metrics_exporter


from opencensus.ext.azure.log_exporter import AzureEventHandler, AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer


stats = stats_module.stats
view_manager = stats.view_manager


config_integration.trace_integrations(["logging"])
config_integration.trace_integrations(["requests"])


logger = logging.getLogger(__name__)
handler = AzureLogHandler(
    connection_string="InstrumentationKey=c5225e0c-f17a-4c75-8425-9c79e588626f;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
)
handler.setFormatter(logging.Formatter("%(traceId)s %(spanId)s %(message)s"))
logger.addHandler(handler)

logger.addHandler(
    AzureEventHandler(
        connection_string="InstrumentationKey=c5225e0c-f17a-4c75-8425-9c79e588626f;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    )
)

logger.setLevel(logging.INFO)


exporter = metrics_exporter.new_metrics_exporter(
    enable_standard_metrics=True,
    connection_string="InstrumentationKey=c5225e0c-f17a-4c75-8425-9c79e588626f;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/",
)
view_manager.register_exporter(exporter)


tracer = Tracer(
    exporter=AzureExporter(
        connection_string="InstrumentationKey=c5225e0c-f17a-4c75-8425-9c79e588626f;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    ),
    sampler=ProbabilitySampler(1.0),
)
app = Flask(__name__)


middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(
        connection_string="InstrumentationKey=c5225e0c-f17a-4c75-8425-9c79e588626f;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    ),
    sampler=ProbabilitySampler(rate=1.0),
)


app.config.from_pyfile("config_file.cfg")

if "VOTE1VALUE" in os.environ and os.environ["VOTE1VALUE"]:
    button1 = os.environ["VOTE1VALUE"]
else:
    button1 = app.config["VOTE1VALUE"]

if "VOTE2VALUE" in os.environ and os.environ["VOTE2VALUE"]:
    button2 = os.environ["VOTE2VALUE"]
else:
    button2 = app.config["VOTE2VALUE"]

if "TITLE" in os.environ and os.environ["TITLE"]:
    title = os.environ["TITLE"]
else:
    title = app.config["TITLE"]

# Redis Connection to a local server running on the same machine where the current FLask app is running.
r = redis.Redis()

"""
# The commented section below is used while deploying the application with two separate containers -
# One container for Redis and another for the frontend.

# Redis configurations
redis_server = os.environ['REDIS']

try:
    if "REDIS_PWD" in os.environ:
        r = redis.StrictRedis(host=redis_server,
                        port=6379,
                        password=os.environ['REDIS_PWD'])
    else:
        r = redis.Redis(redis_server)
    r.ping()
except redis.ConnectionError:
    exit('Failed to connect to Redis, terminating.')
"""

if app.config["SHOWHOST"] == "true":
    title = socket.gethostname()


if not r.get(button1):
    r.set(button1, 0)
if not r.get(button2):
    r.set(button2, 0)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":

        vote1 = r.get(button1).decode("utf-8")

        with tracer.span(name="Cats Vote") as span:
            print("Cats Vote")

        vote2 = r.get(button2).decode("utf-8")

        with tracer.span(name="Dogs Vote") as span:
            print("Dogs Vote")

        return render_template(
            "index.html",
            value1=int(vote1),
            value2=int(vote2),
            button1=button1,
            button2=button2,
            title=title,
        )

    elif request.method == "POST":
        if request.form["vote"] == "reset":

            r.set(button1, 0)
            r.set(button2, 0)

            vote1 = r.get(button1).decode("utf-8")
            properties = {"custom_dimensions": {"Cats Vote": vote1}}

            logger.info("Cats Vote", extra=properties)

            vote2 = r.get(button2).decode("utf-8")
            properties = {"custom_dimensions": {"Dogs Vote": vote2}}

            logger.info("Dogs Vote", extra=properties)

            return render_template(
                "index.html",
                value1=int(vote1),
                value2=int(vote2),
                button1=button1,
                button2=button2,
                title=title,
            )

        else:

            vote = request.form["vote"]
            r.incr(vote, 1)

            vote1 = r.get(button1).decode("utf-8")
            properties = {"custom_dimensions": {"Cats Vote": vote1}}

            logger.info("Cats Vote", extra=properties)

            vote2 = r.get(button2).decode("utf-8")
            properties = {"custom_dimensions": {"Dogs Vote": vote2}}

            logger.info("Dogs Vote", extra=properties)

            return render_template(
                "index.html",
                value1=int(vote1),
                value2=int(vote2),
                button1=button1,
                button2=button2,
                title=title,
            )


if __name__ == "__main__":
    # comment line below when deploying to VMSS
    app.run() # local
    # uncomment the line below before deployment to VMSS
    # app.run(host='0.0.0.0', threaded=True, debug=True) # remote