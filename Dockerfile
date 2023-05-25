FROM python:3-alpine3.17 as base

RUN apk --no-cache add tzdata libcurl su-exec

FROM base as builder

ENV PYCURL_SSL_LIBRARY=openssl

COPY requirements.txt /requirements.txt

RUN apk add --no-cache --virtual .build-deps build-base curl-dev \
    && pip install --prefix=/install -r /requirements.txt \
    && apk del --no-cache --purge .build-deps \
    && rm -rf /var/cache/apk/*

FROM base

LABEL org.opencontainers.image.description="Upload your invoices from email attachements automatically to Lexoffice." \
      org.opencontainers.image.authors="Maki IT <kontakt@maki-it.de>" \
      org.opencontainers.image.licenses="MIT"

STOPSIGNAL SIGINT

ENV TZ=Europe/Berlin \
    CRON='*/5 * * * *' \
    PYTHONUNBUFFERED=1

WORKDIR /app/
VOLUME /app/config

ARG USER=lexoffice-uploader
RUN adduser --disabled-password --no-create-home $USER

COPY --from=builder /install /usr/local
COPY --chown=$USER:$USER . .

RUN chmod +x /app/docker/entrypoint.sh && \
    chmod +x /app/main.py && \
    rm /app/requirements.txt && \
    chown -R $USER /app

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]
CMD python3 /app/main.py --configfile /app/config/ --continuous --cron "$CRON"