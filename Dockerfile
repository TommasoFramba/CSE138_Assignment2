FROM python:3
COPY . /app
RUN make /app
WORKDIR /app
CMD python3 webserver.py
