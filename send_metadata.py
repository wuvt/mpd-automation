#!/usr/bin/env python2
import requests
import mpd
import os
from select import select
# you need to pip install requests to use this
# Gets the artist, title, album from MPD and POSTs to QT
submit_url = "https://www.wuvt.vt.edu/trackman/api/automation/log"
mpd_password = ""
automation_password = ""
host = "localhost"
port = "6600"
metadata_file = "/tmp/metadata"

# Connect to mpd
def connect():
    client = mpd.MPDClient(use_unicode=True)
    client.idletimeout = None
    # If this errors handle it outside
    client.connect(host, port)
    client.password(mpd_password)
    return client

# Two events are generated for each new song, not sure why but we don't
# want to double log 
def log_if_new(current_track):
    last_id = load_last()
    new_id = int(current_track['id'])
    if new_id != last_id:
        last_id = new_id
        save_last(new_id)
        log_track(current_track)

def main():
    c = connect()
    log_if_new(c.currentsong())
    c.send_idle('player')
    while True:
        can_read = select([c], [], [])[0]
        changes = c.fetch_idle()
        log_if_new(c.currentsong())
        c.send_idle('player')
def save_last(trackid):
    try:
        with open(metadata_file, 'w') as f:
            f.write(str(trackid))
    except Exception as e:
        print("Error writing metadata: " + str(e))



def load_last():
    try:
        if not os.path.exists(metadata_file):
            open(metadata_file, 'w').close()
            return -1
        else:
            with open(metadata_file, 'r') as f:
                try:
                    trackid = int(f.read())
                    return trackid
                except:
                    save_last(str(-1))
                    return -1
    except Exception as e:
        print("Error opening metadata: " + str(e))
        return -1
def log_track(track):

    payload = {}
    try:
        payload['album'] = track['album']
    except:
        payload['album'] = "Not available"

    try:
        payload['title'] = track['title']
    except:
        payload['title'] = "Not available"

    try:
        payload['artist'] = track['artist']
    except:
        payload['artist'] = "Not available"

    payload['password'] = automation_password

    # Not yet supported, there's a server side workaround
    #try:
    #    payload['label'] = track['label']
    #except:
    #    payload['label'] = "Not available"

    print("payload: " + str(payload))
    # POST

    try:
        r = requests.post(submit_url, data=payload)
        if (r.json()['success']):
            print("Track logged succesfully")
        else:
            print("Error: " + r.json()['error'])
    except Exception as e:
        print("Error: " + str(e))

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Error: " + str(e))
