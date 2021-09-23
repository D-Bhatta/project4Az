FROM tiangolo/uwsgi-nginx-flask:python3.6
RUN pip install redis
RUN pip install opencensus
RUN pip install opencensus-ext-azure
RUN pip install opencensus-ext-flask
RUN pip install opencensus-ext-logging
RUN pip install opencensus-ext-requests
RUN pip install flask
# Copy the content of the current directory to the /app of the container
ADD . /app
EXPOSE 80
EXPOSE 443
