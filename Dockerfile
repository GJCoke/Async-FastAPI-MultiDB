# python 3.12
FROM python:3.12

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/*

# set python env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# copy pyproject.toml
COPY pyproject.toml ./

# pip install
RUN pip install -U pip \
    && pip install -e .[dev]

# copy current dir to image src
COPY . /src
ENV PATH "$PATH:/src/scripts"

# create new user and setting permission
RUN useradd -m -d /src -s /bin/bash app \
    && chown -R app:app /src/* && chmod +x /src/scripts/*

# set worker dir and switch app user
WORKDIR /src
USER app

# start server
CMD ["./scripts/run-dev.sh"]
