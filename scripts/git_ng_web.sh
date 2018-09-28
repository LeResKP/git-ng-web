#!/usr/bin/env sh

source env/bin/activate


case "$1" in
  start)
    uwsgi --ini-paste production.ini
    ;;
  stop)
    uwsgi --stop uwsgi.pid
    ;;
  restart)
    $0 stop
    $0 start
    ;;
  *)
    echo "Usage: $0 start/stop";
esac
