FROM ubuntu:22.04
LABEL maintainer=falldog

ARG PY_VER=3.10
ARG NAME=admin
ARG PW=1234
ARG PASSPHRASE=TEST_FOR_DJANGO

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        # debug utility
        vim \
        less \
        \
        curl \
        build-essential \
        software-properties-common \
        python3-distutils \
        pkg-config \
        \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python${PY_VER} python${PY_VER}-dev \
        \
    && rm -rf /var/lib/apt/lists/* \
    \
    && curl https://bootstrap.pypa.io/get-pip.py | python${PY_VER}

RUN set -ex \
    && mkdir -p /code \
    && mkdir -p /pyconcrete-code \
    && ln -sf /usr/bin/python${PY_VER} /usr/bin/python

# install pip requirements
COPY example/django/pye_web/requirements.txt /code/
RUN pip install --no-cache-dir -r /code/requirements.txt

# copy source code
COPY example/django/pye_web/ \
     /code/
COPY . \
     /pyconcrete-code/

# install pyconcrete && compile .pye
RUN set -ex \
    && cd /pyconcrete-code/ \
    && pip \
      install \
      --config-settings=setup-args=-Dpassphrase=${PASSPHRASE} \
      --config-settings=setup-args=-Dmode=lib \
      --config-settings=setup-args=-Dinstall-cli=true \
      . \
    && pyecli compile \
        --source=/code/ \
        --pye \
        --remove-py \
        --remove-pyc \
        -i wsgi.py manage.py

WORKDIR /code

# manipulate django with encrypted pye files
RUN set -ex \
    && python manage.py migrate \
    && DJANGO_SUPERUSER_PASSWORD=${PW} python manage.py createsuperuser \
        --username=${NAME} \
        --noinput \
        --email=admin@pyconcrete.test

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
