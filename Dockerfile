# Buster slim base image.
FROM debian:buster-slim
MAINTAINER Swisstopo

RUN groupadd -r geoadmin && useradd -r -s /bin/false -g geoadmin geoadmin


# TODO : add relevant packages
RUN apt-get update && apt-get install apt-utils \
  ; DEBIAN_FRONTEND=noninteractive apt-get install -y --upgrade ca-certificates \
  ; DEBIAN_FRONTEND=noninteractive apt-get install -y -o Dpkg::Options::="--force-confold" \
  bash \
  curl \
  g++ \
  make \
  python3.7-minimal \
  python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY "./requirements.txt" "/app/requirements.txt"

RUN pip3 install -r requirements.txt

COPY "./" "/app/"

RUN chown -R geoadmin:geoadmin /service_qr_code/app
USER geoadmin

EXPOSE 8080

# Use a real WSGI server
ENTRYPOINT ["python3", "wsgi.py"]
