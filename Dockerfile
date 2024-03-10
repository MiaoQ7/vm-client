FROM python:3.9.11

WORKDIR /project
COPY requirements.txt .

VOLUME /project/logs /project/vfs /tmp

RUN pip install -r requirements.txt

ENTRYPOINT ["supervisord", "-n", "-c", "/project/docker/supervisord.conf"]
