#!/usr/bin/env python2
import os
import codecs
import chardet
import logging
import mpd
import sys

"""
Usage: ./playlist_to_mpd.py <identifier>
Clears MPD's playlist and adds everything from playlist.m3u
"""

playlist_path = "/mnt/mckillican/automation/"

logging.basicConfig(level=logging.DEBUG)

# Read playlist file
identifier = sys.argv[1]


#with open(playlist_file) as f:
playlist_file = None
    
for prefix in ["Cycle_", "CYCLE_"]:
    for extension in [".m3u", ".M3U"]:
        guessfile = prefix + identifier + extension
        guesspath = os.path.join(playlist_path, guessfile)
        if os.path.isfile(guesspath):
            playlist_file = guesspath
            break
    if playlist_file is not None:
        # Escape the guessing game
        break

if playlist_file == None:
    logging.Error("Unable to find playlist specified by " + identifier)
    exit()

with open(playlist_file) as f:
    encoding = chardet.detect(f.read())
    logging.debug("Detected character set as " + encoding["encoding"] + " with " + str(encoding["confidence"]) + " certainty")
    if encoding["confidence"] > 0.9:
        encoding = encoding["encoding"]
    else:
        logging.debug("Not certain enough, falling back on iso-8859-1")
        encoding = "iso-8859-1"
with open(playlist_file) as f:
    playlist_items = f.readlines()
   

logging.debug("Reencoding playlist")
for i in xrange(len(playlist_items)):
    utfitem = playlist_items[i].decode(encoding).encode("utf8")
    if playlist_file[0:4] != 'unix':
        logging.debug("Non unix m3u, making unix file path")
        playlist_items[i] = utfitem.replace('\\','/').replace('Z:/','/mnt/mckillican/automation/')
    else:
        playlist_items[i] = utfitem

 
# Connection
logging.debug("Connecting to MPD")
client = mpd.MPDClient()
client.timeout = 10 
client.idletimeout = None
client.connect("localhost", 6600)

logging.debug("MPD Client Ver: " + client.mpd_version)

# Update client in case anything has changed in automation recently
logging.debug("Updating MPD")
try:
    client.update()
except:
    pass


# clear stored playlist of the same name if it exists
playlist_name = os.path.basename(playlist_file)
logging.debug("New playlist: " + playlist_name)
(root, ext) = os.path.splitext(playlist_name)
playlist_name = root

if playlist_name in [playlist["playlist"] for playlist in client.listplaylists()]:
    logging.debug("Clearing old version of the playlist")
    client.playlistclear(playlist_name)
else:
    logging.debug("No previous playlist found")

logging.info("Updating playlist: " + playlist_name)

# add files from the given playlist into an MPD-stored playlist.
logging.debug("Adding {0} tracks".format(len(playlist_items)))
for track in playlist_items:
    if track[:7] == '#EXTINF' or track[:7] == '#EXTM3U':
        continue
    reltrack = os.path.relpath(track, '/mnt/mckillican/automation/').rstrip()
    logging.debug("adding: " + reltrack)
    try:
        client.playlistadd(playlist_name, reltrack)
    except:
	logging.info("Could not add: " + reltrack)


# clear playlist
logging.info("Switching playlist: " + playlist_name)
logging.debug("Clearing current playlist except currently playing song")
#client.clear()
status = client.status()
client.delete(0, int(status["song"]))
status = client.status()
client.load(playlist_name)
logging.debug("Loading new playlist: " + playlist_name)

client.delete((1, status["playlistlength"]))

logging.debug("Closing client")
client.close() 
