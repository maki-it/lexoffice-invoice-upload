FROM python:3-alpine as base

RUN apk --no-cache add tzdata libcurl

FROM base as builder

ENV PYCURL_SSL_LIBRARY=openssl

COPY requirements.txt /requirements.txt

RUN apk add --no-cache --virtual .build-deps build-base curl-dev \
    && pip install --prefix=/install -r /requirements.txt \
    && apk del --no-cache --purge .build-deps \
    && rm -rf /var/cache/apk/*

FROM base

ENV TZ=Europe/Berlin \
    INTERVALL=120

COPY --from=builder /install /usr/local
COPY . /app/
WORKDIR /app/
VOLUME /app/config

RUN chmod +x /app/docker/entrypoint.sh && \
    chmod +x /app/main.py && \
    rm /app/config.ini

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]
CMD python3 -u /app/main.py --config /app/config/ --continuous --intervall $INTERVALL