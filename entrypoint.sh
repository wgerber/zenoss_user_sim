#!/usr/bin/env bash
pid=0

# SIGTERM-handler
term_handler() {
  echo "Received SIGTERM! Killing $pid."
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; term_handler' SIGTERM SIGINT

# run application
python -u sim.py "$@" &
pid="$!"

# wait indefinetely
while true
do
  tail -f /dev/null & wait ${!}
done
