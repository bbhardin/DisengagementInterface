from multiprocessing.spawn import spawn_main

import subprocess

import threading

import time


#from agents.navigation.global_route_planner import GlobalRoutePlanner
#from agents.navigation import generate_traffic

from commentary.commentary_controller import ComentaryController

from examples.DReyeVR_utils import DReyeVRSensor

def start_server():
    cmd = "c:\\Applications\\code\\carla\\Build\\UE4Carla\\0.9.13-dirty\\WindowsNoEditor\\CarlaUE4.exe -vr"
    #os.system(cmd)
    #time.sleep(5)
    subprocess.call(cmd, shell=False)

def generate_traffic():
    cmd = "python3 C:\\Applications\\code\\carla\\PythonAPI\\examples\\generate_traffic.py -n 30"
    #os.system(cmd)
    #time.sleep(5)
    subprocess.call(cmd, shell=False)

def main():

    try:
        #connect to Carla server
        
        thread = threading.Thread(target=start_server)
        thread.start()
        time.sleep(10)
        thread2 = threading.Thread(target=generate_traffic)
        thread2.start()
        print("Generated traffic")
        
    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")

        #actor_list = world.get_actors()
        #client.stop_recorder()
        #print('\ndestroying %d actors' % len(actor_list))
        #client.apply_batch_sync([carla.command.DestroyActor(x) for x in actor_list])

if __name__ == "__main__":
    main()