ARG BUILD_FROM=python:3.12-slim
FROM ${BUILD_FROM}

ARG ODYSSEUS_REF=main
ARG INSTALL_OPTIONAL=false
ARG BUILD_VERSION=0.3.6
ARG BUILD_ARCH=amd64

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ODYSSEUS_DATA_DIR=/data/odysseus \
    FASTEMBED_CACHE_PATH=/data/odysseus/fastembed \
    HF_HOME=/data/odysseus/huggingface \
    HUGGINGFACE_HUB_CACHE=/data/odysseus/huggingface

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        dnsutils \
        file \
        git \
        iproute2 \
        iputils-ping \
        jq \
        less \
        libicu-dev \
        libssl-dev \
        nano \
        nodejs \
        npm \
        openssh-client \
        pkg-config \
        procps \
        python3-venv \
        ripgrep \
        sudo \
        tmux \
        unzip \
        vim-tiny \
        zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone --depth 1 --branch "${ODYSSEUS_REF}" https://github.com/pewdiepie-archdaemon/odysseus.git odysseus

WORKDIR /opt/odysseus

COPY patch_odysseus.py /tmp/patch_odysseus.py
RUN python /tmp/patch_odysseus.py /opt/odysseus

RUN pip install -r requirements.txt \
    && if [ "${INSTALL_OPTIONAL}" = "true" ]; then pip install -r requirements-optional.txt; fi

COPY ingress_proxy.py /opt/odysseus/ingress_proxy.py
COPY install-dotnet-sdk.sh /usr/local/bin/install-dotnet-sdk
COPY run.sh /run.sh
RUN chmod +x /run.sh \
    && chmod +x /usr/local/bin/install-dotnet-sdk \
    && mkdir -p /data/odysseus /data/logs /data/odysseus/fastembed /data/odysseus/huggingface

EXPOSE 7000 8099

CMD ["/run.sh"]
