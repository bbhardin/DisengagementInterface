from multiprocessing.spawn import spawn_main
import os
import random
import subprocess
import sys
import threading
import carla
import time
import logging
import argparse
from datetime import datetime

#from agents.navigation.global_route_planner import GlobalRoutePlanner
#from agents.navigation import generate_traffic

from commentary.commentary_controller import ComentaryController

# from examples.DReyeVR_utils import DReyeVRSensor

def start_server():
    # TODO: ADD BACK -VR TO THIS
    cmd = "c:\\Applications\\ben_code\\carla\\Build\\UE4Carla\\0.9.13-dirty\\WindowsNoEditor\\CarlaUE4.exe"
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

    argparser.add_argument(
        "--map",
        default="",
        help="map to load if not using a scenario (default: not set)",
    )
    argparser.add_argument(
        '-a', '--announce',
        default=7,
        type=int,
        help="distance (in meters) from junction before announcement is made"
    )

    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=10,
        type=int,
        help='number of vehicles (default: 10)')

    argparser.add_argument(
        '-s', '--samplingresolution',
        metavar='S',
        default=2,
        type=int,
        help='distance between successive waypoints in meters')

    argparser.add_argument(
        '-min_dist', '--min_dist',
        default=100,
        type=int,
        help='minimum distance limit of planned route, default is 100 meters ')

    # TODO: ADD BACK TOWN10HD
    argparser.add_argument(
        '-t', '--town',
        metavar='Town04',
        default="Town04",
        help='number of vehicles (default: 10)')

    argparser.add_argument(
        '-d', '--delay',
        metavar='D',
        type=int,
        default=30,
        help='number of ticks before scenario is processed,(default: 40)')

    argparser.add_argument(
        '-ob', '--observe',
        metavar='O',
        default="true",
        help='announce observation, if set to true, agents close to the ego are announced. Default is true')

    argparser.add_argument(
        '-pre_announce', '--pre_announce',
        metavar='-PA',
        default="true",
        help='add additional level of satnav action announcement. If set to true, pre announcement is made before \
        getting to the junction, and then another anouncement is made at the junction. Default is set to true')

    argparser.add_argument(
            '-e', '--error',
            type=int,
            default=1,
            help='add noise to detections in explanation. 0. Gneral and not specific 1. no error 2. introduce error')

    argparser.add_argument(
        '-m','--dualmode',
        default="true",
        help="mode of explanations, when set to true, exlanations are generated from the explainer model, where the model \
            fails to generate explanations, the ground truth from carla is used to generate explanation using some rules. \
                When set to false, the no explanation is provided where the model fails.")

    argparser.add_argument(
        '-f','--filename',
        default="",
        help="log file to load. Must be provided")
    
    argparser.add_argument(
        '-l','--logname',
        default="",
        help="recorded log file to load. Must be provided")

    argparser.add_argument(
        '-x', '--time-factor',
        metavar='X',
        default=1.0,
        type=float,
        help='time factor (default 1.0)')
    argparser.add_argument(
        '-i', '--ignore-hero',
        action='store_true',
        help='ignore hero vehicles')
    argparser.add_argument(
        '--spawn-sensors',
        action='store_true',
        help='spawn sensors in the replayed world')

    args = argparser.parse_args()

    try:
        #connect to Carla server
        
        thread = threading.Thread(target=start_server)
        thread.start()
        time.sleep(10)
        client = carla.Client(args.host, args.port)
        client.set_timeout(60.0)
        print("listening to server %s:%s", args.host, args.port)
        #world = client.get_world()
        #actor_list, spawn_points = spawn_actors(args, client, world)

        # TODO: CHANGE BACK TO TOWN10HD
        world = client.load_world("Town04")
        ego_actor = None
        
        #actor_list, spawn_points = spawn_actors(args, client, world)
        
        _map = world.get_map()
        
        #global_planner = GlobalRoutePlanner(_map, sampling_resolution)

        #actor_list = world.get_actors()
        
        #Get the global  route from ego's current position to a chosen destination
        #global_route, global_route_cmd, route_list = global_planner.trace_route(ego_origin, ego_destination)

        #Draw the route path on the Spectator window and the PyGame window 
        #draw_plan_on_map(world, global_route, ego_origin, ego_destination)
        
        #Create a commentary controller object. This object listens to the server using the on_tick() \
        # method from the world object.
        #The ticking is done in the roads-recorder code.
        #The  commentary controller class listens for navigation plans e.g., turn left and turn right;
        # stimulus driven actions e.g., stop, move, and lane change actions; and then triggers the commentary service
        #which further handles plan commentary or explanation generation procedures. 
        # blueprint_library = world.get_blueprint_library()
        # tesla_model3 = blueprint_library.filter('Volkswagen')[1]
        # print(tesla_model3)

        # TODO: ADD BACK
        # commentary_controller = ComentaryController(world, _map, [], args)
        # log_name = args.logname.split('.')[0]
        # dated_name = "c:/applications/code/userstudy/logs/userdata/" + log_name + "_" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".txt"
        # f = open(dated_name, "w")
        # f.write("")
        # f.close()
        #This tick procedure can also be implemented in a while loop with a delay.
        #world.wait_for_tick()

        # sensor = DReyeVRSensor(world)
        #generate_traffic.main(walker=15)

        # TODO: ADD BACK
        # if  args.logname == "":
        #     print("Error! Record log is not provided!")
        #     try:
        #         sys.exit(0)
        #     except SystemExit:
        #         os._exit(0)
        # file_dir = 'c:/applications/code/study_scenarios/latest/final/' + args.logname
        # #print(file_dir)
        # sim_start_time = 0
        # duration = 0
        # if args.logname == 'general_log_new.log':
        #     sim_start_time = 0
        #     duration = 213
        # elif args.logname == 'error_log_new.log':
        #     sim_start_time = 0
        #     duration = 256
        # elif args.logname == 'specific_log_new.log':
        #     sim_start_time = 0
        #     duration = 272

        # # set the time factor for the replayer
        # client.set_replayer_time_factor(args.time_factor)

        # # set to ignore the hero vehicles or not
        # client.set_replayer_ignore_hero(args.ignore_hero)

        # replay the session

        # TODO: ADD BACK
        #client.replay_file(file_dir, sim_start_time, duration, 0)
        # commentary_controller.get_data(sensor, dated_name, args)

    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")

        #actor_list = world.get_actors()
        #client.stop_recorder()
        #print('\ndestroying %d actors' % len(actor_list))
        #client.apply_batch_sync([carla.command.DestroyActor(x) for x in actor_list])
        if world != None:
            world.destroy()
        
if __name__ == "__main__":
    main()