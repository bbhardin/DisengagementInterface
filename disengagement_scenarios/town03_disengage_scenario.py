import carla
import time
# from srunner.scenariomanager.scenarioatomics.atomic_behaviors import *
# from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import *
# from srunner.scenarios.basic_scenario import BasicScenario
# from srunner.tools.scenario_helper import *
import random
import math
import json

from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.basic_agent import BasicAgent
from agents.navigation.behavior_agent import BehaviorAgent

from disengagement_scenarios.carla_painter import CarlaPainter

class NearWarningScenario():

    #def __init__(self, world, ego_vehicle, config, timeout=60):
        #super().__init__("PedestrianCrossingScenario", ego_vehicle, config, world, timeout)
        #self.timeout = timeout

        # self._pedestrian = None
        # self._pedestrian_walk_start = carla.Location(x=50, y=-1, z=0)
        # self._pedestrian_walk_end = carla.Location(x=50, y=5, z=0)

        # Create a pedestrian crossing actor
        # self._pedestrian = self._create_pedestrian()

        # Setup the route for the ego vehicle
        # self.route = self._create_route(config)

    def get_angle_between_waypoints(wp1, wp2):
        """
        Calculate the angle between two waypoints.
        """
        dx = wp2.transform.location.x - wp1.transform.location.x
        dy = wp2.transform.location.y - wp1.transform.location.y
        angle = math.atan2(dy, dx)
        return math.degrees(angle)

    def is_turning(wp1, wp2, wp3, turn_threshold=20):
        """
        Check if the vehicle is turning by comparing the angles between consecutive waypoints.
        If the angle difference exceeds the `turn_threshold`, it's considered a turn.
        """
        angle1 = NearWarningScenario.get_angle_between_waypoints(wp1, wp2)
        angle2 = NearWarningScenario.get_angle_between_waypoints(wp2, wp3)
        angle_diff = abs(angle1 - angle2)
        return angle_diff > turn_threshold


    def run_scenario(town_map, world, ego_vehicle, client):
        print("setting up the scenario and path to follow!")
        sampling_resolution = 2
        grp = GlobalRoutePlanner(town_map, sampling_resolution) # maybe world should be town_map
        #grp.setup()

        # Todo: abstract some of this to the parent caller so that I don't have to repeat code
        #       for every scenario. Can pass the spawn point to run_scenario method for instance

        # Go to VehicleSpawnPoint157
        spawn_points = town_map.get_spawn_points()
        # Spawn points are literally just transforms. They have no names.
        # # home_location = None
        # for index, point in enumerate(spawn_points):
        #     print("spawn point %s", spawn_points[index])
            # if (point.id == "VehicleSpawnPoint157"):
            #     home_location = point.location

        # TODO: Add some error checking here?
        #_location = spawn_points[157]
        # print("spawn point %s", home_location)
        driveway_location = carla.Location(x=87.365, y=-40.179, z=0.278)
        #home_location = town_map.transform_to_geolocation(home_location)
        #test_location = carla.Location(x=0, y=0, z=10)
        #start_location = carla.Location()
        spawn_point_157 = carla.Location(x=102.849, y=63.711, z=1.0)
        spawn_point_17 = carla.Location(x=102.849, y=66.711, z=0.02)
        location_1 = carla.Location(x=145.426, y=65.575, z=0.02)
        location_2 = carla.Location(x=18.796, y=130.234, z=0.02)
        location_3 = carla.Location(x=4.988, y=46.7459, z=0.02)
        location_4 = carla.Location(x=9.259, y=-119.455, z=0.02)
        location_5 = carla.Location(x=67.818, y=-133.752, z=8.01)
        location_6 = carla.Location(x=136.308, y=-131.928, z=8.01)
        location_7 = carla.Location(x=149.654, y=-85.847, z=8.01)
        location_8 = carla.Location(x=99.284, y=-76.950, z=8.02)
        location_8_v2 = carla.Location(x=148.417, y=-20.695, z=0.097)
        location_9 = carla.Location(x=77.557, y=-20.808, z=0.83)
        location_10 = carla.Location(x=31.038, y=-7.893, z=0.02)
        location_11 = carla.Location(x=-62.416, y=-139.950, z=0.02)
        location_12 = carla.Location(x=-88.310, y=-13.032, z=0.02)
        location_13 = carla.Location(x=-120.684, y=37.113, z=0.02)
        location_14 = carla.Location(x=-145.674, y=9.336, z=0.02)
        location_15 = carla.Location(x=-101.066, y=-136.672, z=0.02)
        location_16 = carla.Location(x=-16.481, y=-197.942, z=0.02)
        location_17 = carla.Location(x=67.540, y=-195.973, z=0.02)
        location_18 = carla.Location(x=84.192, y=-204.755, z=0.02) # Police barracade failure situation
        location_19 = carla.Location(x=12.926, y=193.666, z=0.02)
        location_20 = carla.Location(x=5.441, y=147.183, z=0.02)
        location_21 = carla.Location(x=170.514, y=83.198, z=0.02)
        #  Return to home then
        #  location_22 = carla.Location(x=, y=, z=0.02)
        # location_23 = carla.Location(x=, y=, z=0.02)




        #home_transform = carla.Transform(location=home_location, rotation=carla.Rotation())
        # point_2 = carla.Location()


        print("about to spawn the ego vehicle at home")
        car_transform = carla.Transform(spawn_point_157, carla.Rotation(0, 0, 0))
        #car_transform = carla.Transform(location_13, carla.Rotation(0, 140, 0))
        ego_vehicle.set_transform(car_transform)

        #ego_vehicle.destroy()
        #ego_vehicle = SpawnActor(ego_bp, home_transform)

        route = grp.trace_route(spawn_point_157, location_4)
        # waypoint_list = []
        # for waypoint in range(len(route[0])):
        #     print("idk any more  %s ", route[0][waypoint][0])
        #     waypoint_list.append(route[0][waypoint][0])

        # Todo: trace all segments of the route
        points = []
        for waypoint in route:
            # print("drawing %s", waypoint[0].transform.location)
            loc = waypoint[0].transform.location
            world.debug.draw_string(loc, '^', draw_shadow=False,
                                    color=carla.Color(r=0, g=0, b=255), life_time=320.0,
                                    persistent_lines=True)
            points.append([loc.x, loc.y, loc.z])

        # Convert waypoints to json and save so that our frontend can read
        #    the route on scene load.
        data = {}
        data["waypoints"] = points
        print(data)
        # Check if the file is accessible (not locked) and ready to be written to
        with open("C:/Applications/ben_code/waypoints03.json", "w") as f:
            json.dump(data, f)
            # Do I need to close the file now?


        # Set up the steps the vehicle will take to follow the route
        print("Setting up the agent")

        settings = world.get_settings()
        # settings.fixed_delta_seconds = 0.05
        settings.synchronous_mode = False
        world.apply_settings(settings)

        agent = BasicAgent(ego_vehicle, 20, )
        #agent.set_target_speed(20)
        agent.set_global_plan(route, stop_waypoint_creation=False, clean_queue=True)
        agent.follow_speed_limits(False)
        agent.ignore_stop_signs(False)
        agent.ignore_traffic_lights(True) # TODO CHANGE THIS BACK TO FALSE
        
        
        # This seems to be a problem
        agent.set_destination(location_3)

        #ego_vehicle.set_autopilot(True)


        # I need to set this outside the scenario so
        # that we can spawn other actors
        print("Beginning to follow route")
        dest_index = 2  # We skip the first destination since it's already programmed
                        #   this behaviour should be modified to make more sense
        destinations = [location_1, location_2, location_3, location_4, location_5, location_6,
                        location_7, location_8_v2, location_10, location_11, location_12,
                        location_13, location_14, location_15, location_16, location_17, location_18,
                        location_19, location_20, location_21]
        #destinations = [location_13, location_14, location_15, location_16, location_17, location_18,
                        #location_19, location_20, location_21]
        # destinations = [location_1]
        destinations_2 = [location_4, location_5, location_6]
        

        #traffic_manager = client.get_trafficmanager(8000)
        #traffic_manager.vehicle_percentage_speed_difference(ego_vehicle, 85)
        #ego_vehicle.set_autopilot(True, traffic_manager.get_port())

        # Adjust specific TrafficManager settings for the vehicle
        # traffic_manager.ignore_lights_percentage(ego_vehicle, 50)  # 50% chance the vehicle will ignore traffic lights
        # traffic_manager.ignore_walkers_percentage(ego_vehicle, 0)  # The vehicle will respect pedestrians 100%
        # traffic_manager.random_left_lanechange_percentage(ego_vehicle, 30)  # 30% chance of random left lane changes
        # traffic_manager.random_right_lanechange_percentage(ego_vehicle, 30)  # 30% chance of random right lane changes
        # traffic_manager.vehicle_percentage_speed_difference(ego_vehicle, -10) 

        # traffic_manager.set_path(ego_vehicle, destinations_2)
        # traffic_manager.auto_lane_change(ego_vehicle, True)
        # traffic_manager.global_percentage_speed_difference(-300)

        waypoints = agent._local_planner._waypoints_queue
        for waypoint in waypoints:
            world.debug.draw_string(waypoint[0].transform.location, 'f', draw_shadow=False,
                                    color=carla.Color(r=0, g=255, b=0), life_time=320.0,
                                    persistent_lines=True)
        em_stop = False

        print("before the painter")
        painter = CarlaPainter('localhost', 8081)
        print("after the painter")
        ego_loc = ego_vehicle.get_location()
        trajectories = [[]]

        while True:

            trajectories[0].append([ego_loc.x, ego_loc.y, ego_loc.z])
            painter.draw_polylines(trajectories)
            ego_velocity = ego_vehicle.get_velocity()
            velocity_str = "{:.2f}, ".format(ego_velocity.x) + "{:.2f}".format(ego_velocity.y) \
                    + ", {:.2f}".format(ego_velocity.z)
            painter.draw_texts([velocity_str], [[ego_loc.x, ego_loc.y, ego_loc.z+20.0]], size=20)
            
            #             [[ego_location.x, ego_location.y, ego_location.z + 10.0]], size=20)
            # ego_vehicle.set_autopilot(True, traffic_manager.get_port())
            # if agent.done():
            #     print("Agent is done!")
            #     break



            # control = carla.VehicleControl()
            # control.throttle = 0.0
            # control.brake = 50.0
            # agent.add_emergency_stop(control)

            if agent.done():

                # Set a new destination
                agent.set_destination(destinations[dest_index])

                # Are we at a spot where we should disengage?
                if (dest_index == 2):
                    print('Disengagement')

                    # Bring the vehicle to a stop
                    ego_vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0, hand_brake=False))
                    #agent.set_target_speed(0)
                    em_stop = True # Overwrite the set speed to 15 that happens at turns

                    # Show the user where to drive next

                    # Re-engage the automation once reach the correct waypoint
                    
                #     # Nice, ok now we just have to have a way for the user to reactivate it.
                #     # TODO: how can we ensure that the user drives it in the correct direction.
                #     #time.sleep(1)
                #     # route_2 = grp.trace_route(location_4, location_6)
                #     # agent.set_global_plan(route_2, stop_waypoint_creation=True, clean_queue=True)
                #     agent.set_destination(location_2)
                #     em_stop = True # seems that em stop has to occur while the agent has a 
                #         #       destination. Cannot occur while agent.done() is true.
                
                # print("set a new destination")
                # dest_index += 1
                # if (dest_index == len(destinations)):
                #     print("finished all the disengagements")
                #     break
                # print("The target has been reached, searching for another target")

            if (em_stop):
                print("Applying em stop")
                # control = carla.VehicleControl()
                # control.throttle = 0.0
                # control.brake = 50.0
                # agent.add_emergency_stop(control)
                # ego_vehicle.apply_control(control)
                #ego_vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0, hand_brake=False))
                agent.set_target_speed(0)
                ego_vehicle.apply_control(agent.run_step())
            else:
                waypoints = agent._local_planner._waypoints_queue
                # Check if the agent is turning
                if len(waypoints) > 2:
                    wp1, wp2, wp3 = waypoints[0][0], waypoints[1][0], waypoints[2][0]
                    if NearWarningScenario.is_turning(wp1, wp2, wp3, 10):
                        #print("Approaching a turn, slowing down. %s", wp1)
                        agent.set_target_speed(20)  # Slow down for the turn
                    else:
                        agent.set_target_speed(50)
                        #print("not approaching turn ")
                ego_vehicle.apply_control(agent.run_step())
            #print("%s", ego_veh())

            # Use the below code section to stop automation 
            # distance = ego_vehicle.get_location().distance(destinations[dest_index])
            # if distance < 10.0:
            #     print("close and done!")
            #     ego_vehicle.set_autopilot(False)
            #     # Need to stop the vehicle? Well disengage wouldn't do that..
            #     time.sleep(30)
            #     print('restarted')
            #     ego_vehicle.set_autopilot(True)
            #     dest_index +=1 
            

            world.tick()
        # while True:    
            # print("driving you know") 
            # distance = ego_vehicle.get_location().distance(destinations[dest_index])
            # #if agent.done():
            # # print("distance %s", distance)
            # ego_vehicle.apply_control(agent.run_step())
            # if agent.done():
            #     # Iterate to the next destination or stop if we are done
            #     print("arrived!, going next")
            #     #agent.set_destination(random.choice(spawn_points).location)
            #     #route = grp.trace_route(location_1, location_2) # Todo probably remove
            #     #gent.set_global_plan(route, stop_waypoint_creation=True, clean_queue=True)
            #     agent.set_destination(destinations[dest_index])
            #     # ?print("distance to next %s", distance)
            #     dest_index += 1
            #     if (dest_index == len(destinations)):
            #         print("arrived for good")
            #         break
            
            # world.tick()

        print("broke out of the loop")

    # def _create_pedestrian(self):
    #     # Define pedestrian blueprint and spawn point
    #     pedestrian_bp = self.world.get_blueprint_library().find('walker.pedestrian.0001')
    #     pedestrian_spawn_point = carla.Transform(self._pedestrian_walk_start)
    #     pedestrian_actor = self.world.spawn_actor(pedestrian_bp, pedestrian_spawn_point)
    #     return pedestrian_actor

    # def _create_route(self, config):
    #     # Define a simple route for the ego vehicle
    #     route = [config.trigger_points[0].location,
    #              carla.Location(x=80, y=0, z=0)]
    #     return route

    # def _create_behavior(self):
    #     # Define the behavior sequence for the scenario

    #     # Step 1: Ego vehicle follows the route
    #     driving_to_goal = WaypointFollower(self.ego_vehicle, target_speed=30)

    #     # Step 2: Pedestrian starts crossing the road
    #     pedestrian_crossing = WalkToLocation(self._pedestrian, self._pedestrian_walk_end)

    #     # Step 3: Ego vehicle must stop if pedestrian is too close
    #     stop_condition = InTriggerDistanceToVehicle(self._pedestrian, self.ego_vehicle, distance=10)

    #     # Step 4: Ego vehicle stops for pedestrian to pass
    #     stop_for_pedestrian = StopVehicle(self.ego_vehicle, self._pedestrian_walk_end, 0)

    #     # Step 5: Ego vehicle resumes driving after pedestrian has crossed
    #     resume_driving = WaypointFollower(self.ego_vehicle, target_speed=30)

    #     # Define the sequence of actions
    #     root = py_trees.composites.Sequence("PedestrianCrossingSequence")
    #     root.add_child(driving_to_goal)
    #     root.add_child(stop_condition)
    #     root.add_child(pedestrian_crossing)
    #     root.add_child(stop_for_pedestrian)
    #     root.add_child(resume_driving)

    #     return root

    # def _create_test_criteria(self):
    #     # Define test criteria, e.g., checking if the ego vehicle has reached the destination
    #     goal_reached = InTriggerDistanceToLocation(self.ego_vehicle, self.route[-1], distance=5)
    #     return [goal_reached]

    # def terminate(self):
    #     """
    #     Clean up the actors and reset the world state.
    #     """
    #     if self._pedestrian is not None:
    #         self._pedestrian.destroy()
    #     super(PedestrianCrossingScenario, self).terminate()