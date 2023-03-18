#!/bin/sh

set -e

trap "echo Exiting...; exit 0" EXIT TERM

BASE_DIR="/app"
CONF_DIR="$BASE_DIR/config"
APP_USER=lexoffice-uploader

if [[ "$*" =~ 'python' ]]; then

    if ! [ -d "$CONF_DIR" ]; then
        mkdir "$CONF_DIR"
        chown -R $APP_USER "$CONF_DIR"
    fi

    cd "$BASE_DIR"

    # Check if directory is empty
    if [ -z "$(ls -A $CONF_DIR 2>/dev/null)" ]
    then
        # Check if directory is writeable
        if [ -w "$CONF_DIR" ]
        then
            # Create config when directory is empty
            echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: No config file found in $CONF_DIR. I will generate one for you.\nPlease change the settings to your needs and start the container again.\n"
            python3 $BASE_DIR/main.py --generate --configfile $CONF_DIR/config.ini
            chown -R $APP_USER "$CONF_DIR"
            exit
        else
            echo "Error: $CONF_DIR is not writeable! Permissions are"
            stat -c '%A %U:%G %n' $CONF_DIR
            echo "In numeric:"
            stat -c '%a %u:%g %n' $CONF_DIR
            exit 1
        fi
    fi

    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] Files in $CONF_DIR:"
    ls -A $CONF_DIR

    # convert `/bin/sh -c "command"` to `command`
    if [ $# -gt 1 ] && [ x"$1" = x"/bin/sh" ] && [ x"$2" = x"-c" ]; then
    shift 2
    eval "set -- $1"
    fi

    # Disable glob (*) expansion
    set -f

    su-exec $APP_USER "$@"
else
    su-exec $APP_USER "$@"
fi