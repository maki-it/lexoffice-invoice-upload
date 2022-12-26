#!/bin/sh

set -e

trap "echo Exiting...; exit 0" EXIT TERM

if [[ "$*" =~ 'appstart' ]]; then
    BASE_DIR="/app"
    CONF_DIR="$BASE_DIR/config"

    if ! [ -d "$CONF_DIR" ]; then
    mkdir "$CONF_DIR"
    fi

    cd "$BASE_DIR"

    if [ -z "$(ls -A $CONF_DIR 2>/dev/null)" ]
    then
        echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: No config file found in $CONF_DIR. I will generate one for you.\nPlease change the settings to your needs and start the container again.\n"
        python3 $BASE_DIR/main.py --generate --config $CONF_DIR/config.ini
        exit
    fi

    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] Files in $CONF_DIR:"
    ls -A $CONF_DIR

    # convert `/bin/sh -c "command"` to `command`
    # if [ $# -gt 1 ] && [ x"$1" = x"/bin/sh" ] && [ x"$2" = x"-c" ]; then
    # shift 2
    # eval "set -- $1"
    # fi

    # exec "$@"
    exec "python3 /app/main.py --config /app/config/ --continuous --intervall $INTERVALL"
else
    exec "$@"
fi