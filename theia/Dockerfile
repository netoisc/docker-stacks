FROM ubuntu:18.04 AS builder

# install development tools
# hadolint ignore=DL4006
RUN apt-get update \
 && apt-get install -y \
    curl \
    sudo \
    build-essential \
    jq \
    vim \
 && curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - \
 && apt-get install -y \
    nodejs \
 && npm install -g yarn

# add theia installation file
COPY package.json run_theia.sh /theia-app/
RUN chmod +x /theia-app/run_theia.sh

# build theia
WORKDIR /theia-app
RUN yarn \
 && NODE_OPTIONS="--max_old_space_size=4096" yarn theia build \
 && yarn autoclean --init \
 && echo *.ts >> .yarnclean \
 && echo *.ts.map >> .yarnclean \
 && echo *.spec.* >> .yarnclean \
 && yarn autoclean --force \
 && yarn cache clean

# create debian package
RUN npm run build-deb

# transfer debian package to a new clean image and install theia
FROM illumidesk/base-notebook:latest

ENV NODE_OPTIONS="--max_old_space_size=4096"
ENV NODE_VERSION=10.21.0
ENV NVM_VERSION=0.35.3
ENV NVM_DIR=/usr/local/nvm
ENV NODE_PATH="${NVM_DIR}/v${NODE_VERSION}/lib/node_modules"
ENV NODE_LIB_PATH="${NVM_DIR}/v${NODE_VERSION}/lib"
ENV PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}/bin:${PATH}"
ENV PATH="${NVM_DIR}/v${NODE_VERSION}/lib/node_modules/.bin:${PATH}"
ENV THEIA_DEFAULT_PLUGINS=local-dir:plugins

USER root

WORKDIR /tmp

COPY --from=builder /theia-app/illumidesk-theia_0.1.0_all.deb /tmp/
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - \
 && apt-get install -y /tmp/illumidesk-theia_0.1.0_all.deb \
 && rm /tmp/illumidesk-theia_0.1.0_all.deb
 
## NVM
# https://stackoverflow.com/questions/25899912/how-to-install-nvm-in-docker
# Set debconf to run non-interactively
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install nvm with node and npm
RUN mkdir -p "${NVM_DIR}" \
 && curl "https://raw.githubusercontent.com/creationix/nvm/v${NVM_VERSION}/install.sh" | sudo -E bash \
 && . "${NVM_DIR}/nvm.sh" \
 && nvm install "${NODE_VERSION}" \
 && nvm alias default "${NODE_VERSION}" \
 && nvm use default

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Build lab extensions that may have been included
RUN jupyter lab build

# copy jupyter notebook config
COPY jupyter_notebook_config.py /etc/jupyter/jupyter_notebook_config.py

# fix conda, /etc/jupyter and home directory permissions as root
RUN fix-permissions /etc/jupyter \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "${HOME}"

USER "${NB_UID}"

WORKDIR "${HOME}"
