# Buster slim python 3.7 base image.
FROM python:3.7-slim-buster
ENV HTTP_PORT 8080
RUN groupadd -r geoadmin && useradd -r -s /bin/false -g geoadmin geoadmin


# HERE : install relevant packages
RUN pip3 install pipenv \
    && pipenv --version

COPY Pipfile* /tmp/
RUN cd /tmp && \
    pipenv install --system --deploy --ignore-pipfile

WORKDIR /app
COPY --chown=geoadmin:geoadmin ./ /app/

ARG GIT_HASH=unknown
ARG GIT_BRANCH=unknown
ARG GIT_DIRTY=""
ARG AUTHOR=unknown
ARG TARGET=
LABEL git.hash=$GIT_HASH
LABEL git.branch=$GIT_BRANCH
LABEL git.dirty="$GIT_DIRTY"
LABEL author=$AUTHOR

USER geoadmin

EXPOSE $HTTP_PORT

# Use a real WSGI server
ENTRYPOINT ["python3", "wsgi.py"]
