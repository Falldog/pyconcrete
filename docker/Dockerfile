FROM ubuntu:18.04
LABEL maintainer=falldog

ARG DEBIAN_FRONTEND=noninteractive
ARG PY_VER=3.6

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
        \
    && add-apt-repository -y ppa:deadsnakes/ppa \
	&& rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python${PY_VER} \
        python${PY_VER}-dev \
        python${PY_VER}-distutils \
        \
	&& rm -rf /var/lib/apt/lists/* \
	\
	&& curl https://bootstrap.pypa.io/get-pip.py | python${PY_VER}

RUN set -ex \
    && mkdir -p /code \
    && ln -sf /usr/bin/python${PY_VER} /usr/bin/python

COPY test/requirements.txt /code
RUN set -ex \
    && python${PY_VER} -m pip install --no-cache-dir -r /code/requirements.txt

WORKDIR /code
