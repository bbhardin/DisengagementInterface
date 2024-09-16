from multiprocessing.spawn import spawn_main

import argparse
import carla
import subprocess
import threading

import time


#from agents.navigation.global_route_planner import GlobalRoutePlanner
#from agents.navigation import generate_traffic

from commentary.commentary_controller import ComentaryController

#from examples.DReyeVR_utils import DReyeVRSensor

def start_server():
    # TODO: ADD BACK -vr LATER
    cmd = "c:\\Applications\\ben_code\\carla\\Build\\UE4Carla\\0.9.13-dirty\\WindowsNoEditor\\CarlaUE4.exe"
    #os.system(cmd)
    #time.sleep(5)
    subprocess.call(cmd, shell=False)

def generate_traffic():
    cmd = "python C:\\Applications\\ben_code\\DisengagementInterface\\town03_setup.py -n 30"
    #os.system(cmd)
    #time.sleep(5)
    subprocess.call(cmd, shell=False)

def main():

    argparser = argparse.ArgumentParser(description="CARLA Manual Control Client")
    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )

    # argparser.add_argument(
    #     "--map",
    #     default="",
    #     help="map to load if not using a scenario (default: not set)",
    # )
    # argparser.add_argument(
    #     '-a', '--announce',
    #     default=7,
    #     type=int,
    #     help="distance (in meters) from junction before announcement is made"
    # )

    # argparser.add_argument(
    #     '-n', '--number-of-vehicles',
    #     metavar='N',
    #     default=10,
    #     type=int,
    #     help='number of vehicles (default: 10)')

    # argparser.add_argument(
    #     '-s', '--samplingresolution',
    #     metavar='S',
    #     default=2,
    #     type=int,
    #     help='distance between successive waypoints in meters')

    # argparser.add_argument(
    #     '-min_dist', '--min_dist',
    #     default=100,
    #     type=int,
    #     help='minimum distance limit of planned route, default is 100 meters ')

    argparser.add_argument(
        '-t', '--town',
        metavar='Town03',
        default="Town03",
        help='number of vehicles (default: 10)')

    # argparser.add_argument(
    #     '-d', '--delay',
    #     metavar='D',
    #     type=int,
    #     default=30,
    #     help='number of ticks before scenario is processed,(default: 40)')

    # argparser.add_argument(
    #     '-ob', '--observe',
    #     metavar='O',
    #     default="true",
    #     help='announce observation, if set to true, agents close to the ego are announced. Default is true')

    # argparser.add_argument(
    #     '-pre_announce', '--pre_announce',
    #     metavar='-PA',
    #     default="true",
    #     help='add additional level of satnav action announcement. If set to true, pre announcement is made before \
    #     getting to the junction, and then another anouncement is made at the junction. Default is set to true')

    # argparser.add_argument(
    #         '-e', '--error',
    #         type=int,
    #         default=1,
    #         help='add noise to detections in explanation. 0. Gneral and not specific 1. no error 2. introduce error')

    # argparser.add_argument(
    #     '-m','--dualmode',
    #     default="true",
    #     help="mode of explanations, when set to true, exlanations are generated from the explainer model, where the model \
    #         fails to generate explanations, the ground truth from carla is used to generate explanation using some rules. \
    #             When set to false, the no explanation is provided where the model fails.")

    # argparser.add_argument(
    #     '-f','--filename',
    #     default="",
    #     help="log file to load. Must be provided")
    
    # argparser.add_argument(
    #     '-l','--logname',
    #     default="",
    #     help="recorded log file to load. Must be provided")

    # argparser.add_argument(
    #     '-x', '--time-factor',
    #     metavar='X',
    #     default=1.0,
    #     type=float,
    #     help='time factor (default 1.0)')
    # argparser.add_argument(
    #     '-i', '--ignore-hero',
    #     action='store_true',
    #     help='ignore hero vehicles')
    # argparser.add_argument(
    #     '--spawn-sensors',
    #     action='store_true',
    #     help='spawn sensors in the replayed world')

    args = argparser.parse_args()


    try:
        #connect to Carla server
        
        thread = threading.Thread(target=start_server)
        thread.start()
        time.sleep(10)

        client = carla.Client(args.host, args.port)
        client.set_timeout(60.0)
        print("listening to server %s:%s", args.host, args.port)

        world = client.load_world("Town03")
        # ego_actor = None

        _map = world.get_map()

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