ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then \
    su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; \
    fi

RUN su vscode -c "npm install -g aws-cdk-local aws-cdk"
RUN su vscode -c "pip install aws-sam-cli awscli-local aws-sam-cli-local"
