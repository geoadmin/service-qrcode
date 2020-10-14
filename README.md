# service-qrcode

| Branch | Status |
|--------|-----------|
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoibVJMdm9sbXA4cU1YcWtFMml1UVQwQ2tmdzQ3Z0ZsOFBjVDlsb1NNNTFwZURlWE9qdENiVytId0VzVkJpblBvTmxqVEllSEt0cnlVcXNNR2pqRTNESjRNPSIsIml2UGFyYW1ldGVyU3BlYyI6IkdsNE1FbkZka0hqTFFscjAiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoibVJMdm9sbXA4cU1YcWtFMml1UVQwQ2tmdzQ3Z0ZsOFBjVDlsb1NNNTFwZURlWE9qdENiVytId0VzVkJpblBvTmxqVEllSEt0cnlVcXNNR2pqRTNESjRNPSIsIml2UGFyYW1ldGVyU3BlYyI6IkdsNE1FbkZka0hqTFFscjAiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) |

## Table of content

- [Description](#description)
- [Dependencies](#dependencies)
- [Service API](#service-api)
- [Local Development](#local-development)
- [Deployment](#deployment)

## Description

A simple REST Microservice that returns a QR code from a given URL, using Flask and Gunicorn, with docker containers as a mean of deployment.

## Dependencies

This service doesn't have any external dependencies.

## Service API

This service has two endpoints that are summarized below

- [checker GET](#checker-get)
- [generate POST](#generate-post)

A detailed descriptions of the endpoints can be found in the [OpenAPI Spec](openapi.yaml).

### Staging Environments

| Environments | URL |
|--------------|-----|
| DEV          | [https://service-qrcode.bgdi-dev.swisstopo.cloud/v4/qrcode/](https://service-qrcode.bgdi-dev.swisstopo.cloud/v4/qrcode/)  |
| INT          | [https://service-qrcode.bgdi-int.swisstopo.cloud/v4/qrcode/](https://service-qrcode.bgdi-int.swisstopo.cloud/v4/qrcode/)  |
| PROD         | [https://service-qrcode.bgdi-prod.swisstopo.cloud/v4/qrcode/](https://service-qrcode.bgdi-int.swisstopo.cloud/v4/qrcode/) |

### checker GET

This is a simple route meant to test if the server is up.

| Path | Method | Argument | Response Type |
|------|--------|----------|---------------|
| /v4/qrcode/checker | GET | - | application/json |

### generate POST

This route takes an url in the json payload, check if the hostname and domain are part of allowed names and domains, then
create a QR Code from that URL and return it in a json answer.

| Path | Method | Argument | Content Type | Content | Response Type |
|------|--------|----------|--------------|---------|---------------|
| /v4/qrcode/generate | POST | - | application/json | `{"url": "https://map.geo.admin.ch"}` | image/png |

## Local Development

### Make Dependencies

The **Make** targets assume you have **bash**, **curl**, **tar**, **docker** and **docker-compose** installed.

### Setting up to work

First, you'll need to clone the repo

    git clone git@github.com:geoadmin/service-qrcode.git

Then, you can run the setup target to ensure you have everything needed to develop, test and serve locally

    make setup

That's it, you're ready to work.

### Linting and formatting your work

In order to have a consistent code style the code should be formatted using `yapf`. Also to avoid syntax errors and non
pythonic idioms code, the project uses the `pylint` linter. Both formatting and linter can be manually run using the
following command:

    make format-lint

**Formatting and linting should be at best integrated inside the IDE, for this look at
[Integrate yapf and pylint into IDE](https://github.com/geoadmin/doc-guidelines/blob/master/PYTHON.md#yapf-and-pylint-ide-integration)**

### Test your work

Testing if what you developed work is made simple. You have four targets at your disposal. **test, serve, gunicornserve, dockerrun**

    make test

This command run the integration and unit tests.

    make serve

This will serve the application through Flask without any wsgi in front.

    make gunicornserve

This will serve the application with the Gunicorn layer in front of the application

    make dockerrun

This will serve the application with the wsgi server, inside a container.
To stop serving through containers,

    make shutdown

Is the command you're looking for.

## Deployment

This service is to be deployed to the Kubernetes cluster once it is merged.

TO DO: give instructions to deploy to kubernetes.

### Deployment configuration

The service is configured by Environment Variable:

| Env         | Default               | Description                            |
|-------------|-----------------------|----------------------------------------|
| LOGGING_CFG | logging-cfg-local.yml | Logging configuration file             |
