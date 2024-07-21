#!/usr/bin/env bash

stty -echoctl

adv() {
   read -r -p "pybox: name? " name
   if [ -f "adv/${name}.mp3" ]; then
      mpv --volume=170 "adv/${name,,}.mp3"
   else
      mpv --volume=170 "adv/radio.mp3"
   fi
}

action() {
   tput setaf 1
   echo "pybox: SIGINT caught ..."
   tput sgr0
   read -r -p "pybox: kill? [y/a/s/N] " yn
   case $yn in
   [Yy]*)
      sleep 1
      pkill python
      exit 0
      ;;
   [Aa]*) adv ;;
   [Ss]*) echo >"$tmp" ;;
   *) echo "" ;;
   esac
}

trap 'action' SIGINT

tmp="./pybox.tmp"
while true; do
   rm -f "$tmp"
   alacritty --working-directory "$PWD" -e bash -c ".venv/bin/python pybox.py" &
   # check tmp exists
   while [ ! -f "$tmp" ]; do
      sleep 1
   done
   # safe wait
   sleep 1
done
