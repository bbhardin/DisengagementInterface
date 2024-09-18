import carla
# from srunner.scenariomanager.scenarioatomics.atomic_behaviors import *
# from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import *
# from srunner.scenarios.basic_scenario import BasicScenario
# from srunner.tools.scenario_helper import *

from agents.navigation.global_route_planner import GlobalRoutePlanner


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


    def run_scenario(town_map, world, ego_vehicle):
        print("setting up the scenario and path to follow!")
        sampling_resolution = 2
        grp = GlobalRoutePlanner(town_map, sampling_resolution) # maybe world should be town_map

        home_location = carla.Location(x=8630.0, y=4110.0, z=1.0)
        #test_location = carla.Location(x=0, y=0, z=10)
        location_1 = carla.Location(x=1700.0, y=12680.0, z=0.0)

        home_transform = carla.Transform(location=home_location, rotation=carla.Rotation())
        # point_2 = carla.Location()

        route = grp.trace_route(home_location, location_1)

        print("about to spawn the ego vehicle at home")
        ego_bp = world.get_blueprint_library().find('harplab.dreyevr_vehicle.teslam3')
        
        SpawnActor = carla.command.SpawnActor
        ego_vehicle.set_location(home_location)
        #ego_vehicle.destroy()
        #ego_vehicle = SpawnActor(ego_bp, home_transform)

        # for waypoint in route:
        #     world.debug.draw_string(waypoint[0].transform.location, '^', draw_shadow=False,
        #                             color=carla.Color(r=0, g=0, b=255), life_time=120.0,
        #                             presistent_lines=True)



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