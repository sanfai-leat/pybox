import logging
import os
import sys
import threading
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
    with open("id.lock", "w") as fs:
        fs.write(f"{id}\n")


def fade_in(mp, max, step, fade):
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        for vol in range(0, max + step, step):
            mp._set_property("volume", vol)
            time.sleep(fade / (max / step))


def fade_out(mp, max, step, delay):
    t = threading.current_thread()
    while getattr(t, "do_run", True):
        for vol in range(max, -step, -step):
            mp._set_property("volume", vol)
            time.sleep(fade / (max / step))


def video_available(video_id):
    try:
        ydl = yt_dlp.YoutubeDL({"quiet": True})
        ydl.extract_info(video_id, download=False)
        return True
    except yt_dlp.DownloadError as e:
        logging.error(f"Video not available: {e}")
        return False


if os.path.isfile("id.lock"):
    with open("id.lock", "r") as fs:
        id = int(fs.read().splitlines()[0])
else:
    id = 0
    lock_id(id)

fade = 4.0
step = 5
playlist = df()
adv = mpv.MPV()
player = mpv.MPV(
    ytdl=True,
    ytdl_format="bestaudio",
    player_operation_mode="pseudo-gui",
    script_opts="osc-layout=box,osc-seekbarstyle=bar,osc-deadzonesize=0,osc-minmousemove=3",
    input_default_bindings=True,
    input_vo_keyboard=True,
    osc=True,
)

while True:
    adv_out = threading.Thread(target=fade_out, args=(adv, 100, step, fade))
    player_in = threading.Thread(target=fade_in, args=(player, 60, step, fade))
    player_out = threading.Thread(target=fade_out, args=(player, 60, step, fade))
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
        adv._set_property("volume", 100)
        if os.path.isfile(f"adv/{name.lower()}.mp3"):
            adv.play(f"adv/{name.lower()}.mp3")
            time.sleep(2)
        else:
            adv.play("adv/youre.mp3")
        player.play(url)
        logging.info(f"Now playing {id+1}/{id_max}:::{name}:::{title}")
        logging.info(
            f"Next one    {'='*(len(str(id+1)+str(id_max))+3)}>{playlist.name[id+1]}:::{playlist.title[id+1]}"
        )
        player.wait_until_playing()
        player_in.start()
        adv_out.start()
        time.sleep(fade)
        player_in.do_run = False
        adv_out.do_run = False
        while player._get_property("playtime-remaining") > 21:
            time.sleep(1)
        player_out.do_run = True
        player_out.start()
        time.sleep(fade * 0.9)
        player_out.do_run = False
    except Exception as err:
        logging.warning(f"Python mpv play: {err}")
    id += 1
    lock_id(id)
