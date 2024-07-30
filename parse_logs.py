
import json
import time
from agents.tools.misc import text_to_speech
from commentary.commentary_service import CommentaryService

data = None
def get_data(filename):
    
    with open(filename) as f:
        global data
        data = json.load(f)
        #print(sdata)
    if data != None:
        print(data.keys())

filename = 'logs/log1.json'
get_data(filename)

key_ind = 0
start_secs = time.time()
keys = list(data.keys())
def process_data(data):
    global key_ind
    if key_ind < len(keys):
        key = keys[key_ind]# in keys:
        print(key)
        global start_secs
        print(start_secs, data[key]['seconds'])
        if time.time() >= start_secs + data[key]['seconds']:
            if data[key]['commentary'] != None and data[key]['commentary'] != '':
                text_to_speech(data[key]['commentary'])
            elif data[key]['f_explanation'] != None and data[key]['f_explanation'] != '':
                text_to_speech(data[key]['f_explanation'])
            key_ind += 1
            #start_secs = time.time()


while True:
    process_data(data)
    #time.sleep(1)