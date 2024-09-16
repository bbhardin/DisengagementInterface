#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

""" Module with auxiliary functions. """

import json
import math
import os
import numpy as np
import carla
import time

from gtts import gTTS
from pygame import mixer
import pygame
import playsound
pygame.init()
import pyttsx3

def decode_commentary(command):
    if command == "RIGHT":
        return "Turn right"
    elif command == "LEFT":
        return "Turn left"
    elif command == "STRAIGHT":
        return "Go straight"
    elif command == "CHANGELANELEFT":
        return "change to left lane"
    elif command == "CHANGELANERIGHT":
        return "change to right lane"


def decode_navigation_command(command):
    if command == "RIGHT":
        return 5
    elif command == "LEFT":
        return 6
    elif command == "STRAIGHT":
        return 1
    elif command == "CHANGELANELEFT":
        return 3
    elif command == "CHANGELANERIGHT":
        return 2

def create_log_data(timestamp, town, ego_details, trafficlight_obj, comment, explanation, dynamic_actors):
    timestamp = str(timestamp)
    json_obj = {}
    json_obj[timestamp] = {}
    json_obj[timestamp]["town"] = town
    json_obj[timestamp]["ego_lane"] = [ego_details[0], ego_details[1]]
    json_obj[timestamp]["ego_action"] =  ego_details[3]
    json_obj[timestamp]["ego_plan"] =  ego_details[2]
    json_obj[timestamp]["ego_related_traffic_light"] = trafficlight_obj
    json_obj[timestamp]["commentary"] = comment
    json_obj[timestamp]["f_explanation"] = explanation
    json_obj[timestamp]["other_actors"] = dynamic_actors
    json_obj[timestamp]["f_chunks"] = ""
    json_obj[timestamp]["f_dist"] = []
    
    #write_log(json_obj, file_path='logs/xai_log.json')
    return json_obj

# def write_log2(json_obj, file_path):

#     if not os.path.isfile(file_path):
#         with open(file_path, mode='w') as f:
#             json.dump(json_obj, f, indent=2)
#     else:
#         with open(file_path, "r+") as edr_file:
            
#             # edr_file.seek(0)
#             # # If file is not empty then append '\n'
#             # edr_file.write("\n")
#             # # Append text at the end of file
#             # edr_file.write(json.dumps(json_obj))

#             #data
#             #data.update(json_obj)
#             edr_file.seek(-1,2)
#             edr_file.write(json.dumps(json_obj))
#             edr_file.close()


def write_log_as_text(data, filepath):
    with open(filepath, "a+") as file_object:
        file_object.seek(0)
        file_object.write(',\n')
        file_object.write(data)

#a more efficient method to append logs to json file without loading to memory
def write_log(data, filepath):
 
    """
    Append data in JSON format to the end of a JSON file.
    NOTE: Assumes file contains a JSON object (like a Python
    dict) ending in '}'. 
    :param filepath: path to file
    :param data: dict to append
    """

    # edit the file in situ - first open it in read/write mode
    with open(filepath, 'r+') as f:

        f.seek(0,2)        # move to end of file
        index = f.tell()    # find index of last byte

        # walking back from the end of file, find the index 
        # of the original JSON's closing '}'
        while not f.read().startswith('}'):
            index -= 1
            if index == 0:
                raise ValueError("can't find JSON object in {!r}".format(filepath))
            f.seek(index)

        # starting at the original ending } position, write out
        # the new ending
        

        f.seek(index)
        if index <= 2:
            # construct JSON fragment as new file ending
            new_ending = json.dumps(data)[1:-1] + "}\n"
            f.write(new_ending)
        else:
            # construct JSON fragment as new file ending
            new_ending = ", " + json.dumps(data)[1:-1] + "}\n"
            f.write(new_ending)
        


def text_to_speech(msg):
    
    try:
        myobj = gTTS(text=msg, lang='en', slow=False)

        # Saving the converted audio in a mp3 file named msg.mp3
        myobj.save("msg1.mp3")
        # Play from Buffer
        #playsound.playsound('msg.mp3')
        mixer.init()
        mixer.music.load('msg1.mp3')
        mixer.music.play()
        os.remove('msg2.mp3')

    except:
        myobj = gTTS(text=msg, lang='en', slow=False)

        # Saving the converted audio in a mp3 file named msg.mp3
        myobj.save("msg2.mp3")
        # Play from Buffer
        #playsound.playsound('msg.mp3')
        mixer.init()
        mixer.music.load('msg2.mp3')
        mixer.music.play()
        os.remove('msg1.mp3')
    #     pass
        #pyttsx3.speak(msg)
        
    #time.sleep(100)
    #os.remove('msg.mp3')

                
def get_actor_class(actor):
    bp_parts = actor.type_id.split(".")
    actor_class = bp_parts[0]

    return actor_class

def get_actor_type(actor):
    bp_parts = actor.type_id.split(".")
    actor_type = bp_parts[0]
    if actor_type == "vehicle":
        name = bp_parts[-1]
        if name == "crossbike" or name == "omafiets" or name == "century":
            actor_type = "Cyclist"
        elif name == "ninja" or name == "yzf" or name == "low_rider" or name == "zx125":
            actor_type = "MotorBike"
        elif name == "police" or name == "chargercop2020"  or  name == "charger_police" \
            or name == "charger_police_2020" or name == "ambulance" or name ==  "firetruck":
            actor_type = "EmVehicle"
        elif name == "carlacola":
            actor_type = "Vehicle"
        elif name == "t2":
            actor_type = "Vehicle"
        else:
            actor_type = "Vehicle"

    elif actor_type == "walker":
        actor_type = "Pedestrian"
    
    elif actor_type == "traffic":
        actor_type = "traffic light"

    return actor_type


# Get the transform of the front of the ego
def get_ego_front_transforms(ego_actor):
    ego_transform = ego_actor.get_transform()
    ego_forward_vector = ego_transform.get_forward_vector()
    ego_extent = ego_actor.bounding_box.extent.x
    ego_front_transform = ego_transform
    ego_front_transform.location += carla.Location(
        x=ego_extent * ego_forward_vector.x,
        y=ego_extent * ego_forward_vector.y,
    )
    return ego_front_transform


def get_lane_number(current_lane_info):
    """ 
    Obtain the lane number of a waypoint. First lane from the right being 1
    """
    num_lane_changes = 0
    
    if current_lane_info != None:
            
        if(str(current_lane_info.lane_type) == 'Driving'):
            while(True):
                
                if current_lane_info != None:
                    if(str(current_lane_info.lane_type) == 'Driving'):
                        
                        num_lane_changes += 1

                        current_lane_info = current_lane_info.get_right_lane()

                    else:
                        break
                else:
                    break

    return num_lane_changes


def draw_plan_on_map(world, global_route, ego_origin, ego_destination, colour):
    """
    Draw waypoints on the map
    """

    # world.debug.draw_point(ego_origin, size=0.2, life_time=3, \
    #         persistent_lines=True, color=carla.Color(0, 255, 0))

    world.debug.draw_point(ego_destination, size=0.2, life_time=1000, \
        persistent_lines=True, color=carla.Color(255, 0, 0))


    for gwpt in global_route:
        world.debug.draw_point(gwpt[0].transform.location, size=0.05, life_time=1000, \
        persistent_lines=True, color=colour)
    
    #print("Plan length is..: ", len(global_route))
    return len(global_route)


def is_within_distance(target_transform, reference_transform, max_distance, angle_interval=None):
    """
    Check if a location is both within a certain distance from a reference object.
    By using 'angle_interval', the angle between the location and reference transform
    will also be tkaen into account, being 0 a location in front and 180, one behind.

    :param target_transform: location of the target object
    :param reference_transform: location of the reference object
    :param max_distance: maximum allowed distance
    :param angle_interval: only locations between [min, max] angles will be considered. This isn't checked by default.
    :return: boolean
    """
    target_vector = np.array([
        target_transform.location.x - reference_transform.location.x,
        target_transform.location.y - reference_transform.location.y
    ])
    norm_target = np.linalg.norm(target_vector)

    # If the vector is too short, we can simply stop here
    if norm_target < 0.001:
        return True

    # Further than the max distance
    if norm_target > max_distance:
        return False

    # We don't care about the angle, nothing else to check
    if not angle_interval:
        return True

    min_angle = angle_interval[0]
    max_angle = angle_interval[1]

    fwd = reference_transform.get_forward_vector()
    forward_vector = np.array([fwd.x, fwd.y])
    angle = math.degrees(math.acos(np.clip(np.dot(forward_vector, target_vector) / norm_target, -1., 1.)))

    return min_angle < angle < max_angle


def draw_waypoints(world, waypoints, z=0.5):
    """
    Draw a list of waypoints at a certain height given in z.

        :param world: carla.world object
        :param waypoints: list or iterable container with the waypoints to draw
        :param z: height in meters
    """
    for wpt in waypoints:
        wpt_t = wpt.transform
        begin = wpt_t.location + carla.Location(z=z)
        angle = math.radians(wpt_t.rotation.yaw)
        end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
        world.debug.draw_arrow(begin, end, arrow_size=0.3, life_time=1.0)



def get_speed(vehicle):
    """
    Compute speed of a vehicle in Km/h.

        :param vehicle: the vehicle for which speed is calculated
        :return: speed as a float in Km/h
    """
    vel = vehicle.get_velocity()

    return 3.6 * math.sqrt(vel.x ** 2 + vel.y ** 2 + vel.z ** 2)

def get_trafficlight_trigger_location(traffic_light):
    """
    Calculates the yaw of the waypoint that represents the trigger volume of the traffic light
    """
    def rotate_point(point, radians):
        """
        rotate a given point by a given angle
        """
        rotated_x = math.cos(radians) * point.x - math.sin(radians) * point.y
        rotated_y = math.sin(radians) * point.x - math.cos(radians) * point.y

        return carla.Vector3D(rotated_x, rotated_y, point.z)

    base_transform = traffic_light.get_transform()
    base_rot = base_transform.rotation.yaw
    area_loc = base_transform.transform(traffic_light.trigger_volume.location)
    area_ext = traffic_light.trigger_volume.extent

    point = rotate_point(carla.Vector3D(0, 0, area_ext.z), math.radians(base_rot))
    point_location = area_loc + carla.Location(x=point.x, y=point.y)

    return carla.Location(point_location.x, point_location.y, point_location.z)



def compute_magnitude_angle(target_location, current_location, orientation):
    """
    Compute relative angle and distance between a target_location and a current_location

        :param target_location: location of the target object
        :param current_location: location of the reference object
        :param orientation: orientation of the reference object
        :return: a tuple composed by the distance to the object and the angle between both objects
    """
    target_vector = np.array([target_location.x - current_location.x, target_location.y - current_location.y])
    norm_target = np.linalg.norm(target_vector)

    forward_vector = np.array([math.cos(math.radians(orientation)), math.sin(math.radians(orientation))])
    d_angle = math.degrees(math.acos(np.clip(np.dot(forward_vector, target_vector) / norm_target, -1., 1.)))

    return (norm_target, d_angle)


def distance_vehicle(waypoint, vehicle_transform):
    """
    Returns the 2D distance from a waypoint to a vehicle

        :param waypoint: actual waypoint
        :param vehicle_transform: transform of the target vehicle
    """
    loc = vehicle_transform.location
    x = waypoint.transform.location.x - loc.x
    y = waypoint.transform.location.y - loc.y

    return math.sqrt(x * x + y * y)


def vector(location_1, location_2):
    """
    Returns the unit vector from location_1 to location_2

        :param location_1, location_2: carla.Location objects
    """
    x = location_2.x - location_1.x
    y = location_2.y - location_1.y
    z = location_2.z - location_1.z
    norm = np.linalg.norm([x, y, z]) + np.finfo(float).eps

    return [x / norm, y / norm, z / norm]


def compute_distance(location_1, location_2):
    """
    Euclidean distance between 3D points

        :param location_1, location_2: 3D points
    """
    x = location_2.x - location_1.x
    y = location_2.y - location_1.y
    z = location_2.z - location_1.z
    norm = np.linalg.norm([x, y, z]) + np.finfo(float).eps
    return norm


def positive(num):
    """
    Return the given number if positive, else 0

        :param num: value to check
    """
    return num if num > 0.0 else 0.0