#!/usr/bin/env bash

# Hide ^C
stty -echoctl

# Function called by trap
skill() {
   tput setaf 1
   printf "pybox: SIGINT caught ..."
   tput sgr0
   sleep 1
   pkill python
   exit 0
}

# Trap SIGINT (Ctrl + C)
trap 'skill' SIGINT

tmp="./pybox.tmp"
while true; do
   rm -f "$tmp"
   .venv/bin/python pybox.py &
   # check tmp exists
   while [ ! -f "$tmp" ]; do
      sleep 0.5
   done
   # check playtime
   while [ "$(cat $tmp)" -gt 35 ]; do
      sleep 1
   done
   # safe wait
   sleep 1
done
