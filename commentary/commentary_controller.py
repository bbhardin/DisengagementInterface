
import json
import os
import random
import sys
import time
import pygame
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.tools.misc import draw_plan_on_map, get_lane_number, get_speed, text_to_speech, write_log, write_log_as_text
from commentary.commentary_service import CommentaryService
import carla

DEVIATED = True

class ComentaryController(object):
    """ This class listens to the server using the on_tick() \
        method from the world object.
        The ticking is done in the roads-recorder code.
        The commentary controller class listens for navigation plans e.g., turn left and turn right;
        stimulus driven actions e.g., stop, move, and lane change actions; and then triggers the commentary service
        which further handles plan commentary or explanation generation procedures.
    """
    
    def __init__(self, world, _map, spawn_points, args):

        self.min_dist_lim = args.min_dist
        random.shuffle(spawn_points)
        self.ego_destination = None
        self.world = world
        self.ego_actor = None
        # Get ego actor by attributes
        actor_list = world.get_actors()
        for actor in actor_list:
            vehs = actor.type_id.split(".")
            if len(vehs) >= 2:
                if "dreyevr.egovehicle" == vehs[-2] + '.' + vehs[-1]: #.attributes:
                    self.ego_actor = actor
                    print("Found Ego ......")
                    break

        #Render Carla spectator window in top-down view
        # new_transform = carla.Transform(carla.Location(x=0, z=220), carla.Rotation(pitch = -85))
        # world.get_spectator().set_transform(new_transform)


        #blueprint = world.get_blueprint_library().filter('vehicle.dreyevr.egovehicle')[0]
        #eg_spawn_point = carla.Transform(carla.Location(x=1, y=2, z=3), carla.Rotation())
        transform1 = carla.Transform(carla.Location(x=3.047784, y=130.210068, z=0.600000), \
                carla.Rotation(pitch=0.000000, yaw=-179.647827, roll=0.000000))
        # transform.location = carla.Location(x=-76.847580, y=-69.724976, z=0.001678)

        transform2 = carla.Transform(carla.Location(x=106.028816, y=67.419983, z=0.600000), \
                            carla.Rotation(pitch=0.000000, yaw=-89.609253, roll=0.000000))

        transform3 = carla.Transform(carla.Location(x=98.800659, y=82.890846, z=0.600000), \
                                carla.Rotation(pitch=0.000000, yaw=90.390709, roll=0.000000))

        #client.get_world().spawn_actor(blueprint, transform)
        #self.ego_actor.set_transform(transform3)


        ego_origin = self.ego_actor.get_transform().location
        self.ego_destination = None
        self.ego_origin = ego_origin
        self.first_ego_origin = ego_origin
        
        #blueprint = world.get_blueprint_library().filter('vehicle.dreyevr.egovehicle')[0]
        #eg_spawn_point = carla.Transform(carla.Location(x=1, y=2, z=3), carla.Rotation()

        #one
        #self.ego_destination = carla.Location(x=-87.276062, y=24.441530, z=0.001312)

        #two
        #self.ego_destination = carla.Location(x=-7.966957, y=66.283257, z=0.001312)

        # #three
        #self.ego_destination = carla.Location(x=-41.853989, y=-30.438610, z=0.001312)

        # #four
        # self.ego_destination = carla.Location(x=62.025547, y=16.905891, z=0.600000)

        self.commentary_object = {}
        self.json_obj = "None"
        self.timestamp = 0
        self.seconds = time.time()
        self.data = None
        self.key_ind = 0
        self.current_secs = None
        self.offset = 0
        self.counter = 0
        self.prev_sec = 0
        self.prev_time = None

    def listen(self, timestamp, world, _map, args):
        pass

    def get_data(self, sensor, dated_name, args):
        # filename = 'logs/log1.json'
        # with open(filename) as f:
        #     self.data = json.load(f)
        #     #print(sdata)
        # if self.data != None:
        #     print(self.data.keys())
        def fetch_exp_log(filename):
            if args.filename == "":
                print("Error: Exp log name is invalid!!!")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            with open(filename) as f:
                self.data = json.load(f)
                #print(sdata)
            if self.data != None:
                print(self.data.keys())


        filename = 'C:/Applications/code/userstudy/'+ args.filename
        fetch_exp_log(filename)

        keys = list(self.data.keys())
        self.prev_time = time.time()
        if args.filename == "logs/log1_new_general.json":
            self.offset = -21
        elif args.filename == "logs/log2_new_error.json":
            self.offset = -14
        elif args.filename == "logs/log3_new_specific.json":
            self.offset = -20
            
        def process_data(data):
            exp_data = {'explanation': '', 'commentary': '', 'recorded_secs':0}
            if self.key_ind < len(keys):
                key = keys[self.key_ind]# in keys:

                if 'location' in data[key]:
                    curr_loc = self.ego_actor.get_transform().location
                    if curr_loc.x < data[key]['location']['x'] + 1 and curr_loc.x > data[key]['location']['x'] - 1:
                        if curr_loc.y < data[key]['location']['y'] + 1 and curr_loc.y > data[key]['location']['y'] - 1:
                        #print("End here....")
                            if data[key]['commentary'] != None and data[key]['commentary'] != '':
                                text_to_speech(data[key]['commentary'])
                                exp_data['commentary'] = data[key]['commentary']
                                #print(data[key]['commentary'], data[key]['seconds'])
                            elif data[key]['f_explanation'] != None and data[key]['f_explanation'] != '':
                                text_to_speech(data[key]['f_explanation'])
                                exp_data['explanation'] = data[key]['f_explanation']

                            exp_data['recorded_secs'] = data[key]['seconds']
                                #print(data[key]['f_explanation'], data[key]['seconds'])
                            self.key_ind += 1
                            self.prev_sec = data[key]['seconds']
                            self.prev_time = time.time()
                                                 
                else:
                    curr_loc = self.ego_actor.get_transform().location
                    #print(time.time() - self.prev_time)
                    if time.time() - self.prev_time >= data[key]['seconds'] - self.prev_sec + self.offset:
                        if data[key]['commentary'] != None and data[key]['commentary'] != '':
                            text_to_speech(data[key]['commentary'])
                            exp_data['commentary'] = data[key]['commentary']
                            print(data[key]['commentary'], data[key]['seconds'])
                            #print(curr_loc)
                        elif data[key]['f_explanation'] != None and data[key]['f_explanation'] != '':
                            text_to_speech(data[key]['f_explanation'])
                            exp_data['explanation'] = data[key]['f_explanation']
                            print(data[key]['commentary'], data[key]['seconds'])

                        exp_data['recorded_secs'] = data[key]['seconds']

                        self.current_secs = None
                        self.key_ind += 1
                        self.prev_sec = data[key]['seconds']
                        self.prev_time = time.time()
                        self.offset = 0
            return exp_data

        def publish_and_print(data):
            
            if self.counter % 2 == 0:
                sensor.update(data)
                #print("################################")
                #print(str(sensor.data['left_indicator_input']) + ":" +str(sensor.data['left_indicator_count']) + "; " + str(sensor.data['right_indicator_input'])\
                #     + ":" +str(sensor.data['right_indicator_count']))
                #print(sensor.data)
                
                #sys.exit()
                self.timestamp = sensor.data['timestamp_carla']
                exp_data = process_data(self.data)

                """
                Listens and checks the world status for changes in snapshots.
                """
                log_data = sensor.data
                log_data['explanation'] = exp_data['explanation']
                log_data['commentary'] = exp_data['commentary']
                log_data['recorded_secs'] = exp_data['recorded_secs']
                write_log_as_text(str(log_data), dated_name)
            self.counter += 1
            if self.counter == 100:
                self.counter == 0
            

        sensor.ego_sensor.listen(publish_and_print)

        while True:
            self.world.tick()
            time.sleep(0.5)
            
    #obtain commentary logs
    def get_data_log(self):
        return self.commentary_object