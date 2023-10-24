# service-qrcode

| Branch | Status |
|--------|-----------|
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoibVJMdm9sbXA4cU1YcWtFMml1UVQwQ2tmdzQ3Z0ZsOFBjVDlsb1NNNTFwZURlWE9qdENiVytId0VzVkJpblBvTmxqVEllSEt0cnlVcXNNR2pqRTNESjRNPSIsIml2UGFyYW1ldGVyU3BlYyI6IkdsNE1FbkZka0hqTFFscjAiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoibVJMdm9sbXA4cU1YcWtFMml1UVQwQ2tmdzQ3Z0ZsOFBjVDlsb1NNNTFwZURlWE9qdENiVytId0VzVkJpblBvTmxqVEllSEt0cnlVcXNNR2pqRTNESjRNPSIsIml2UGFyYW1ldGVyU3BlYyI6IkdsNE1FbkZka0hqTFFscjAiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) |

## Table of content

- [Table of content](#table-of-content)
- [Description](#description)
- [Dependencies](#dependencies)
- [Service API](#service-api)
  - [Staging Environments](#staging-environments)
  - [checker GET](#checker-get)
  - [generate GET](#generate-get)
- [Versioning](#versioning)
- [Local Development](#local-development)
  - [Make Dependencies](#make-dependencies)
  - [Setting up to work](#setting-up-to-work)
  - [Linting and formatting your work](#linting-and-formatting-your-work)
  - [Test your work](#test-your-work)
  - [Docker helpers](#docker-helpers)
- [Deployment](#deployment)
  - [Deployment configuration](#deployment-configuration)

## Description

A simple REST Microservice that returns a QR code from a given URL, using Flask and Gunicorn, with docker containers as a mean of deployment.

## Dependencies

This service doesn't have any external dependencies.

## Service API

This service has two endpoints that are summarized below

- [checker GET](#checker-get)
- [generate GET](#generate-get)

A detailed descriptions of the endpoints can be found in the [OpenAPI Spec](openapi.yaml).

### Staging Environments

| Environments | URL |
|--------------|-----|
| DEV          | [https://sys-map.dev.bgdi.ch/api/qrcode/](https://ssys-map.dev.bgdi.ch/api/qrcode/)  |
| INT          | [https://sys-map.int.bgdi.ch/api/qrcode/](https://sys-map.int.bgdi.ch/api/qrcode/)  |
| PROD         | [https://map.geo.admin.ch/api/qrcode/](https://map.geo.admin.ch/api/qrcode/) |

### checker GET

This is a simple route meant to test if the server is up.

| Path | Method | Argument | Response Type |
|------|--------|----------|---------------|
| /checker | GET | - | application/json |

### generate GET

This route takes an url in the json payload, check if the hostname and domain are part of allowed names and domains, then
create a QR Code from that URL and return it in a json answer.

| Path | Method | Argument | Response Type |
|------|--------|----------|---------------|
| /generate | GET | url: unencoded URL to be QR coded | image/png |

## Versioning

This service uses [SemVer](https://semver.org/) as versioning scheme. The versioning is automatically handled by `.github/workflows/main.yml` file.

See also [Git Flow - Versioning](https://github.com/geoadmin/doc-guidelines/blob/master/GIT_FLOW.md#versioning) for more information on the versioning guidelines.

## Local Development

### Make Dependencies

The **Make** targets assume you have **python3.7**, **pipenv**, **bash**, **curl**, **tar**, **docker** and **docker-compose** installed.

### Setting up to work

First, you'll need to clone the repo

    git clone git@github.com:geoadmin/service-qrcode.git

Then, you can run the `dev` target to ensure you have everything needed to develop, test and serve locally

    make dev

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

This will serve the application with the Gunicorn layer in front of the application. It also add the route prefix `/api/qrcode`.

    make dockerrun

This will serve the application with the wsgi server, inside a container.

### Docker helpers

From each github PR that is merged into `master` or into `develop`, one Docker image is built and pushed on AWS ECR with the following tag:

- `vX.X.X` for tags on master
- `vX.X.X-beta.X` for tags on develop

Each image contains the following metadata:

- author
- git.branch
- git.hash
- git.dirty
- version

These metadata can be read with the following command

```bash
make dockerlogin
docker pull 974517877189.dkr.ecr.eu-central-1.amazonaws.com/service-qrcode:develop.latest

# NOTE: jq is only used for pretty printing the json output,
# you can install it with `apt install jq` or simply enter the command without it
docker image inspect --format='{{json .Config.Labels}}' 974517877189.dkr.ecr.eu-central-1.amazonaws.com/service-qrcode:develop.latest | jq
```

You can also check these metadata on a running container as follows

```bash
docker ps --format="table {{.ID}}\t{{.Image}}\t{{.Labels}}"
```

To build a local docker image tagged as `service-qrcode:local-${USER}-${GIT_HASH_SHORT}` you can
use

```bash
make dockerbuild
```

To push the image on the ECR repository use the following two commands

```bash
make dockerlogin
make dockerpush
```

## Deployment

This service is to be deployed to the Kubernetes cluster. See [geoadmin/infra-kubernetes/services/service-qrcode](https://github.com/geoadmin/infra-kubernetes/tree/master/services/service-qrcode#readme)

### Deployment configuration

The service is configured by Environment Variable:

| Env         | Default               | Description                            |
|-------------|-----------------------|----------------------------------------|
| LOGGING_CFG | `logging-cfg-local.yml` | Logging configuration file           |
| ALLOWED_DOMAINS | `.*` | Comma separated list of regex that are allowed as domain in Origin header |
| CACHE_CONTROL | `public, max-age=31536000` | Cache Control header value of the GET /generate endpoint |
| CACHE_CONTROL_4XX | `public, max-age=3600` | Cache Control header for 4XX responses |
