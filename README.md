# service-qrcode

## Summary of the project
A simple REST microservice meant to return a QR code from an URL, using Flask and Gunicorn, with docker containers as a mean of deployment.

## How to run locally

### dependencies

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

    make lint

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

## Endpoints
all trailing slashes are optionals


### /checker/

#### description of the route
this is a simple route meant to test if the server is up.
#### parameters ####

None

#### expected results

**Success**

    "OK", 200

### /generate/
### /qrcodegenerator/
 /qrcodegenerator/ is the legacy route. This should be kept until the geoadmin viewer no longer requests it.
 Both routes have the exact same comportment.
#### description of the route
This route takes an url, check if the hostname and domain are part of allowed hostnames and domains, shorten it
(through the API's shortener endpoint), then create a QR Code from that shortened URL.
#### parameters ####

url, **String**, Mandatory

#### expected results

**Success**

    a QR code linking to the shortened URL, 200

Alternatively, as the shortener might encounter a temporary hiccup, the following result may happen.

    a QR code linking to the non shortened URL, 200

**Failures**

No url in the request

    "The parameter 'url' is missing from the request", 400

No hostname

    "Could not determine the hostname", 400

Hostname or Domain not part of authorised hosts or domains

    "Shortener can only be used for [ list of allowed domains ] domains or [ list of allowed hosts ] hosts.", 400

Internal Error

    "An error occured during the qrcode generation", 500

## Deploying the project and continuous integration
When creating a PR, terraform should run a codebuild job to test, build and push automatically your PR as a tagged container.

This service is to be deployed to the Kubernetes cluster once it is merged.

TO DO: give instructions to deploy to kubernetes.