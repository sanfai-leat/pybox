import logging
import os
import sys
import time

import mpv
import yt_dlp
from pandas import read_csv

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    filename="pybox.log",
    encoding="utf-8",
    level=logging.DEBUG,
)


def df():
    df = read_csv(
        "playlists/playlist.csv",
        header=None,
        sep=":::",
        names=["name", "title", "url"],
        engine="python",
    )
    return df


def lock_id(id):
    with open("pybox.lock", "w") as fs:
        fs.write(f"{id}\n")


def video_available(video_id):
    try:
        ydl = yt_dlp.YoutubeDL({"quiet": True})
        ydl.extract_info(video_id, download=False)
        return True
    except yt_dlp.DownloadError as e:
        logging.error(f"Video not available: {e}")
        return False


def fade_in(mp, off, max, step, fade):
    mp._set_property("time-pos", off)
    for vol in range(0, max + step, step):
        mp._set_property("volume", vol)
        time.sleep(fade / (max / step))


def fade_out(mp, max, step, fade):
    time.sleep(7)
    for vol in range(max, 30, -step):
        mp._set_property("volume", vol)
        time.sleep(fade / (max / step))


if os.path.isfile("pybox.lock"):
    with open("pybox.lock", "r") as fs:
        id = int(fs.read().splitlines()[0])
else:
    id = 0
    lock_id(id)

player = mpv.MPV(
    ytdl=True,
    ytdl_format="bestaudio",
    player_operation_mode="pseudo-gui",
    script_opts="osc-layout=box,osc-seekbarstyle=bar,osc-deadzonesize=0,osc-minmousemove=3",
    input_default_bindings=True,
    input_vo_keyboard=True,
    osc=True,
)

try:
    playlist = df()
except Exception as err:
    logging.warning(f"Not updating playlist cause: {err}", file=sys.stderr)
    playlist = playlist
id_max = playlist.shape[0]
try:
    url = playlist.url[id]
    name = playlist.name[id]
    title = playlist.title[id]
    while not video_available(url):
        logging.info(f"Skipping  {id}:::{name}::{title}")
        id += 1
        lock_id(id)
        url = playlist.url[id]
        name = playlist.name[id]
        title = playlist.title[id]
except KeyError:
    logging.warning("Playlist finished!")
    print("Playlist finished!")
    sys.exit(0)
try:
    # load track
    player.play(url)
    player.wait_until_playing()
    logging.info(f"Now playing {id+1}/{id_max}:::{name}:::{title}")
    # prepare next
    id += 1
    lock_id(id)
    if id in playlist.name.keys():
        logging.info(
            f"Next one    {'='*(len(str(id)+str(id_max))+3)}>{playlist.name[id]}:::{playlist.title[id]}"
        )
        # fade-in
        fade_in(player, 5, 100, 5, 10.0)
        # wait end
        while True:
            playtime = player._get_property("playtime-remaining")
            if playtime <= 75 and playtime > 70:
                with open("pybox.tmp", "w") as fs:
                    fs.write("")
                while player._get_property("playtime-remaining") > 70:
                    time.sleep(1)
            if playtime <= 70:
                break
            time.sleep(1)
        # fade-out
        fade_out(player, 100, 5, 12.0)
    else:
        logging.warning("Last track in playlist!")
        print("Last track in playlist!")
        # fade-in
        fade_in(player, 5, 100, 5, 10.0)
        # wait end
        playtime = player._get_property("playtime-remaining")
        time.sleep(playtime)
    # shut-down
    player.stop()
    player.quit(code=0)
except Exception as err:
    logging.warning(f"Python mpv play: {err}")
    id += 1
    lock_id(id)
