#!/usr/bin/env bash

# poll.sh
# =======
# bash script to pull Gpoll
# warning: export UUID before run

# update poll responses
touch "old.txt"
touch "diff.txt"
curl -sSL "https://docs.google.com/spreadsheets/d/$UUID/export?format=tsv" |
   sed 's/\t/:::/g' |
   tail -n +2 >"poll.txt"

# diff strategy
[[ -f "old.txt" ]] && (diff -w "old.txt" "poll.txt" | patch "diff.txt")

# translate track to link
echo >>"diff.txt"
while read -r line; do
   if [[ -n "$line" ]]; then
      read -r nick track <<<"$(awk -F ':::' '{print $2, $3}' <<<"$line")"
      echo "[info] searching $nick:::$track"
      yt-dlp --default-search ytsearch1 "$track" --get-id 2>/dev/null |
         sed -E "s|.*|$nick:::$track:::https://www.youtube.com/watch?v=\0|" >>"poll.csv"
   else
      echo "[info] empty diff"
   fi
done <"diff.txt"
rm -f "diff.txt"
mv -f "poll.txt" "old.txt"
