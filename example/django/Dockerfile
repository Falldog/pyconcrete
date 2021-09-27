FROM ubuntu:18.04
LABEL maintainer=falldog

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
    && python setup.py install --passphrase=PASSPHARE \
    && pyconcrete-admin.py compile \
        --source=/code/ \
        --pye \
        --remove-py \
        --remove-pyc \
        -i wsgi.py manage.py

WORKDIR /code

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
