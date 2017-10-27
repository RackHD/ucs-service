#!/bin/bash

. /lib/lsb/init-functions

WORKINGPATH=`pwd`
SUPERVISORD=/usr/local/bin/supervisord
SUPERVISORCTL=/usr/local/bin/supervisorctl
NAME=supervisord
DESC=supervisor
LOGDIR=/var/log/supervisor
PIDFILE=/var/run/$NAME.pid
DODTIME=5
OPTS="-c $WORKINGPATH/supervisord.conf"
USER=`users`

export WORKINGPATH
export LOGDIR
export USER

[ -f $SUPERVISORD ] || exit 0
[ -d "$LOGDIR" ] || mkdir "$LOGDIR"

set -e
check_running_core() {
    pid=$1
    name=$2
    [ -z "$pid" ] && return 1
    [ ! -d /proc/$pid ] &&  return 1
    (cat /proc/$pid/cmdline | tr "\000" "\n"|grep -q $name) || return 1
    return 0
}

check_running() {
    [ ! -f "$PIDFILE" ] && return 1
    pid=`cat $PIDFILE`
    check_running_core $pid $SUPERVISORD || return 1
    return 0
}

force_stop() {
    [ ! -f "$PIDFILE" ] && return
    if check_running ;then
        kill -15 $pid
        # Is it really dead?
        [ -n "$DODTIME" ] && sleep "$DODTIME"s
        if check_running ;then
            kill -9 $pid
            [ -n "$DODTIME" ] && sleep "$DODTIME"s
            if check_running ;then
                echo "Cannot kill $NAME (pid=$pid)!"
                exit 1
            fi
        fi
    fi
    rm -f $PIDFILE
    return 0
}

case "$1" in
    start)
        echo -n "Starting $DESC: "
        start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --exec $SUPERVISORD -- $OPTS
        sleep 1 && [ -f $PIDFILE ] || sleep 1
        if check_running ;then
            echo "$NAME."
        else
            echo "ERROR."
        fi
    ;;
    stop)
        echo -n "Stopping $DESC: "
        start-stop-daemon --stop --quiet --oknodo --pidfile $PIDFILE
        echo "$NAME."
    ;;
    force-stop)
        echo -n "Forcefully stopping $DESC: "
        force_stop
        if ! check_running ;then
            echo "$NAME."
        else
            echo "ERROR."
        fi
    ;;
    restart)
        echo -n "Restarting $DESC: "
        start-stop-daemon --stop --quiet --oknodo --pidfile $PIDFILE
        [ -n "$DODTIME" ] && sleep $DODTIME
        start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --exec $SUPERVISORD -- $OPTS
        echo "$NAME."
    ;;
    status)
        echo -n "$NAME is "
        if check_running ;  then
            echo "running"
        else
            echo "not running."
            exit 1
        fi
        $SUPERVISORCTL status
    ;;
    *)
        echo "Usage: sudo ./ucs-service-ctl.sh {start|stop|restart|status}" >&2
        exit 1
    ;;
esac
exit 0
