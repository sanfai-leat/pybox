#!/usr/bin/env bash

for track in $(awk -F ':::' '{print $3}' playlists/playlist.csv); do
   out="download/$(echo "$track" | sed -E 's/https.*v=(.*)/\1/')"
   [[ -e "$out.opus" ]] || .venv/bin/yt-dlp "$track" -x --audio-format opus --output "$out"
done
sed -E 's/https.*v=(.*)/download\/\1.opus/' playlists/playlist.csv >download/playlist.csv
ln -sf ../download/playlist.csv playlists/playlist.csv
