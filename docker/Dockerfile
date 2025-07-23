FROM ubuntu:22.04
LABEL maintainer=falldog

ARG DEBIAN_FRONTEND=noninteractive
ARG PY_VER=3.10

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
        gpg-agent \
        \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python${PY_VER} \
        python${PY_VER}-dev \
        python${PY_VER}-distutils \
        pkg-config \
        \
    && rm -rf /var/lib/apt/lists/*

# install pip
RUN if [ "${PY_VER}" = "3.7" ] ; then \
        curl https://bootstrap.pypa.io/pip/3.7/get-pip.py | python3.7 ; \
    elif [ "${PY_VER}" = "3.8" ] ; then \
        curl https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 ; \
    else \
        curl https://bootstrap.pypa.io/get-pip.py | python${PY_VER} ; \
    fi

RUN set -ex \
    && mkdir -p /code/tests \
    && ln -sf /usr/bin/python${PY_VER} /usr/bin/python

COPY tests/requirements.txt /code/tests
RUN set -ex \
    && python${PY_VER} -m pip install --no-cache-dir -r /code/tests/requirements.txt

WORKDIR /code
