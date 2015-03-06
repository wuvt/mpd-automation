#!/usr/bin/env python2
import requests
import mpd
import json
import time
# you need to pip install requests to use this
# Gets the artist, title, album from MPD and POSTs to QT

# Connect to mpd
while True:
	client = mpd.MPDClient()
	client.timeout = 10
	client.idletimeout = None
	client.connect("localhost", 6600)

	old_payload = {}
	with open('/tmp/metadata', 'r') as f:
	    try:
		old_payload = json.loads(f.read())    
		print("old payload: " + str(old_payload))
	    except:
		print("No JSON could be decoded from saved metadata")

	payload = {'password':'hunter2'}
	try:
	    payload['album'] = client.currentsong()['album']
	except:
	    payload['album'] = "Not available"

	try:
	    payload['title'] = client.currentsong()['title']
	except:
	    payload['title'] = "Not available"

	try:
	    payload['artist'] = client.currentsong()['artist']
	except:
	    payload['artist'] = "Not available"

	print("new payload: " + str(payload))
	# POST

	if old_payload == payload:
	    print("Track has already been logged. Not updating metadata.")
	else:
	    try:
		r = requests.post('http://www.wuvt.vt.edu/trackman/automation/submit', data=payload)
		print("Metadata updated.")
	    except:
		print("Could not update metadata")

	# Write payload to tempoary file.
	with open('/tmp/metadata', 'w') as f:
	    f.write(json.dumps(payload))

	client.disconnect()
	time.sleep(5)
