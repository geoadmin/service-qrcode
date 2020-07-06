# Buster slim base image.
FROM python:3.7-slim-buster

RUN groupadd -r geoadmin && useradd -r -s /bin/false -g geoadmin geoadmin


# HERE : install relevant packages
# RUN apt-get update && apt-get install -y [packages] \
#  && apt-get clean \
#  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY "./requirements.txt" "/app/requirements.txt"

RUN pip3 install -r requirements.txt

COPY "./" "/app/"

RUN chown -R geoadmin:geoadmin /service_qr_code/app
USER geoadmin

EXPOSE 8080

# Use a real WSGI server
ENTRYPOINT ["python3", "wsgi.py"]