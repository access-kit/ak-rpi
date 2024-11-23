# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV POETRY_VERSION=1.8 \
    POETRY_VIRTUALENVS_CREATE=false

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# install ffmpeg and other dependencies for audio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry install --no-interaction --no-ansi --no-root --no-dev

# Copy Python code to the Docker image
COPY ak_rpi /code/ak_rpi/

ENV PYTHONPATH=/code
ENV PYTHONUNBUFFERED=1

CMD [ "python", "ak_rpi/main.py"]
