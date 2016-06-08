#!/usr/bin/env bash
pid=0

# SIGTERM-handler
term_handler() {
  echo "passing SIGINT to sim"
  if [ $pid -ne 0 ]; then
    kill -SIGINT "$pid"
    wait "$pid"
  fi
  exit 130;
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; term_handler' SIGINT

# run application
python -u sim.py "$@" &
pid="$!"

# wait indefinetely
while true
do
  tail -f /dev/null & wait ${!}
done
