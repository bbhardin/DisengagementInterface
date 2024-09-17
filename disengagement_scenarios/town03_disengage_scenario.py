import carla
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import *
from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import *
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import *

class NearWarningScenario(BasicScenario):

    def __init__(self, world, ego_vehicle, config, timeout=60):
        super().__init__("PedestrianCrossingScenario", ego_vehicle, config, world, timeout)
        self.timeout = timeout

        self._pedestrian = None
        self._pedestrian_walk_start = carla.Location(x=50, y=-1, z=0)
        self._pedestrian_walk_end = carla.Location(x=50, y=5, z=0)

        # Create a pedestrian crossing actor
        self._pedestrian = self._create_pedestrian()

        # Setup the route for the ego vehicle
        self.route = self._create_route(config)