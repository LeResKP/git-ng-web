#!/usr/bin/env sh

SCRIPT_PATH=$( cd "$( dirname "$0" )" && pwd )
LOG_FILE="$SCRIPT_PATH/uwsgi.log"
PID_FILE="$SCRIPT_PATH/uwsgi.pid"
CONF_FILE="$SCRIPT_PATH/production.ini"


source "$SCRIPT_PATH/env/bin/activate"


case "$1" in
  start)
    uwsgi --ini-paste $CONF_FILE -d $LOG_FILE --pidfile $PID_FILE
    ;;
  stop)
    uwsgi --stop $PID_FILE
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  *)
    echo "Usage: $0 start/stop";
esac
