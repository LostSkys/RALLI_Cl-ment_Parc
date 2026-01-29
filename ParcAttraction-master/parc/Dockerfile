FROM node:20-alpine

ARG MY_UID
ARG MY_GID

RUN apk add chromium gettext shadow

RUN if [ "$MY_GID" != "0" ]; then \
    groupadd -g "$MY_GID" customgroup && \
    useradd -l -u "$MY_UID" -g "$MY_GID" node; \
    else \
    echo "Using existing root group"; \
    fi

RUN chown -R "$MY_UID:$MY_GID" /home/node

WORKDIR /home/node/app

