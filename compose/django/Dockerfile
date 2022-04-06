FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR src
COPY . /src

RUN pip install --upgrade pip && \
 pip install -r ./requirements.txt

COPY ./compose/django/start /start
RUN chmod +x /start
RUN sed -i 's/\r$//g' /start

COPY ./compose/django/entrypoint /entrypoint
RUN chmod +x /entrypoint
RUN sed -i 's/\r$//g' /entrypoint

ENTRYPOINT ["/entrypoint"]