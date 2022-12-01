# syntax=docker/dockerfile:1.3
### STAGE 1
FROM python:3-slim-bullseye as base

WORKDIR /install

COPY ./requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install -r requirements.txt

### STAGE 2
FROM base as final

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY --from=base /opt/venv /opt/venv
COPY ./entrypoint.sh ./entrypoint.sh

ENV PATH=/opt/venv/bin:$PATH

ENTRYPOINT [ "./entrypoint.sh" ]
