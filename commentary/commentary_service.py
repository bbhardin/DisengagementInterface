from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.tools.misc import create_log_data, decode_commentary, \
    get_actor_class, get_actor_type, get_ego_front_transforms, \
        get_lane_number, get_speed, is_within_distance, text_to_speech, write_log
from agents.navigation.basic_agent import BasicAgent
from commentary.error_script import get_noised_class
#from commentary.commentary_controller import ComentaryController
from commentary.explainer_controller import NAVIGATION_PLAN_CODES, ExplainerController
from agents.navigation.local_planner import LocalPlanner, RoadOption
from commentary.error_script import get_noised_class
import time

NAVIGATION_ACTIONS = [
    "Stop",
    "TurLft",
    "TurRht",
    "Mov",
    "Mov",
    "LCLft",
    "LCRht"
]

class CommentaryService(object):

    """
    This class provides a more detailed implementation of the plan commentary procedure and the explainer procedure.
    The trigger_commentator method picks the next plan and reads it out. 
    The trigger_explainer method calls the explainer module that utilises a tree-based model to generate factual
    and counterfactual  explanations.
    """

    def __init__(self, timestamp, ego_actor, _map, sampling_resolution, global_route_cmd, route_list, args, seconds):
        self.route_list = route_list
        self.global_route_cmd = global_route_cmd
        self.timestamp = timestamp
        self.ego_actor = ego_actor
        self.sampling_resolution = sampling_resolution
        self._map = _map
        self.args = args
        self.town = args.town
        self.json_obj = {}
        self.seconds = seconds
    

    def trigger_observer(self, world, world_snapshot, ego_current_lane_info, ego_lane_type, search_key):
        
        trafficlight_obj = self.get_tl_object(world, self.ego_actor)
        #print("TRAFFIC LIGHT", trafficlight_obj)
        model_file = "models/rf_model2.pkl"
        exlainer_controller = ExplainerController(model_file, self.args)
        comment = ""
        explanation = "STRAIGHT"
        real_data = None
        ego_action = ""
        ego_plan = "LANEFOLLOW"
        dynamic_actors = []
        if search_key in self.global_route_cmd:
            route_index = self.global_route_cmd[search_key][1]
            if route_index+1 < len(self.route_list):
                comment = str(self.route_list[route_index+1].name)
                explanation = ""
                    
                ego_action = self.route_list[route_index].name
                ego_plan = comment
        dynamic_actors = self.get_other_agents(world, world_snapshot, self.ego_actor)
        #print("DDDYYYAAANAMMIIICCC ...", dynamic_actors)
        ego_lane_num = get_lane_number(ego_current_lane_info)
        #represent the scene and the explanation as a json object and write to log file 
        self.json_obj = create_log_data(self.timestamp, self.town, [ego_lane_type, \
            ego_lane_num, ego_plan, ego_action], trafficlight_obj, \
            comment, explanation, dynamic_actors)

        _, real_data = exlainer_controller.get_model_payload(self.json_obj)
        #comment = decode_commentary(comment)
        comment = ''#decode_commentary(comment)
        if trafficlight_obj != None:
            if trafficlight_obj['status'] == "TLMov":
                
                if self.args.error == 0:
                    comment = "traffic sign ahead"
                elif self.args.error == 1:
                        comment = "green traffic light ahead."
                elif self.args.error == 2:
                    comment = "green traffic light ahead."
                
                text_to_speech(comment)
            else:

                if self.args.error == 0:
                    comment = "traffic sign ahead"
                elif self.args.error == 1:
                        comment = "red traffic light ahead."
                elif self.args.error == 2:
                    comment = 'to be noised red traffic light ahead.'
                #comment = "Red traffic light ahead."
                text_to_speech(comment)

        elif real_data != None:
            #print("HEYYYY ******1 ", real_data['VehLane']['type'])
            if real_data['VehLane']['type'] != "":
                #print("HEYYYY ******2 ", real_data['VehLane']['type'])
                if real_data['VehLane']['type'] == 'EmVehicle':
                    if self.args.error == 0:
                        comment = "vehicle ahead on my lane."
                    elif self.args.error == 1:
                        comment = "Emergency vehicle ahead on my lane."
                    elif self.args.error == 2:
                        comment = get_noised_class('emergency vehicle') + ' ahead on my lane.'

                    #comment = "Emergency vehicle ahead on my lane."
                else:
                    key = ""
                    if real_data['VehLane']['type'] == "EmVehicle":
                        key = "emergency vehicle"
                    elif real_data['VehLane']['type'] == "MotorBike":
                        key = "motor bike"
                    else:
                        key = real_data['VehLane']['type'].lower()

                    if self.args.error == 0:
                        if key == 'pedestrian':
                            comment = "road user ahead on my lane"
                        else:
                            comment = "vehicle ahead on my lane."
                    elif self.args.error == 1:
                        comment = key + " ahead on my lane."
                    elif self.args.error == 2:
                        comment =  get_noised_class(key) + " ahead on my lane."    
                text_to_speech(comment)
            elif real_data['OutgoLane']['type'] != "":
                comment = ''
                if real_data['OutgoLane']['type'] == 'pedestrian':
                    if self.args.error == 0:
                        comment = "road user ahead"
                    elif self.args.error == 1:
                        comment = "pedestrian ahead."
                    elif self.args.error == 2:
                        comment = get_noised_class('pedestrian') + " ahead."
                    text_to_speech(comment)


            # elif real_data['OutgoLane']['type'] != "":
            #     comment = real_data['OutgoLane']['type'] + " on outgoing lane."
            #     text_to_speech(comment)

            # elif real_data['IncomLane']['type'] != "":
            #     comment = real_data['IncomLane']['type'] + " on incoming lane."
            #     text_to_speech(comment)
        self.json_obj[str(self.timestamp) ]['commentary'] = comment

        if comment != '' and comment != None:
            time_diff =  time.time() - self.seconds
            self.json_obj[str(self.timestamp)]['seconds'] = time_diff
            write_log(self.json_obj, filepath='logs/xai_log.json')

        return self.json_obj

    def trigger_commentator(self, world, world_snapshot, ego_current_lane_info, ego_lane_type, search_key, pre_announce=False):
        comment = ""
        if search_key in self.global_route_cmd:
            route_index = self.global_route_cmd[search_key][1]
            if route_index+1 < len(self.route_list):
                
                if self.route_list[route_index+1].name != RoadOption.LANEFOLLOW.name:
                    
                    comment = str(self.route_list[route_index+1].name)
                    explanation = ""
                    if pre_announce == True:
                        if comment == RoadOption.STRAIGHT:
                            text_to_speech(decode_commentary(comment) + " at the junction")
                            comment = decode_commentary(comment) + " at the junction"
                        else:
                            text_to_speech("Prepare to " + decode_commentary(comment))
                            comment = "Prepare to " + decode_commentary(comment)
                    else:
                        text_to_speech(decode_commentary(comment))
                        comment = decode_commentary(comment)
                        
                    ego_action = self.route_list[route_index].name
                    ego_plan = comment
                    dynamic_actors = self.get_other_agents(world, world_snapshot, self.ego_actor)
                    
                    trafficlight_obj = self.get_tl_object(world, self.ego_actor)

                    ego_lane_num = get_lane_number(ego_current_lane_info)
                    
                    self.json_obj = create_log_data(self.timestamp, self.town, [ego_lane_type, \
                        ego_lane_num, ego_plan, ego_action], trafficlight_obj, \
                        comment, explanation, dynamic_actors)

                    #f_explanation, chunks, f_dist = exlainer_controller.explain_factual(self.json_obj)
                    
                    #write_log(self.json_obj, filepath='logs/xai_log.json')

        # else:
        #     ego_origin = self.ego_actor.get_transform().location
        #     #self.reset_map_route(world, self._map, ego_origin, ego_destination)
        
        return self.json_obj
                    
    def trigger_explainer(self, world, world_snapshot, ego_current_lane_info, ego_lane_type, ego_action, search_key):
        #print("GLOBAL ROUTE COMD", self.global_route_cmd)
        ego_plan = None
        #ego_action = None
        if search_key in self.global_route_cmd:
            route_index = self.global_route_cmd[search_key][1]
            if route_index+1 < len(self.route_list):
                #ego_action = self.route_list[route_index].name
                ego_plan = self.route_list[route_index+1].name
            else:
                ego_plan = "LANEFOLLOW"

        else:
            ego_plan = "LANEFOLLOW"

        dynamic_actors = self.get_other_agents(world, world_snapshot, self.ego_actor)
        
        trafficlight_obj = self.get_tl_object(world, self.ego_actor)

        ego_lane_num = get_lane_number(ego_current_lane_info)

        model_file = "models/rf_model2.pkl"
        exlainer_controller = ExplainerController(model_file, self.args)
        comment = ""
        explanation = ""
        #represent the scene and the explanation as a json object and write to log file 
        self.json_obj = create_log_data(self.timestamp, self.town, [ego_lane_type, \
            ego_lane_num, ego_plan, ego_action], trafficlight_obj, \
            decode_commentary(comment), explanation, dynamic_actors)
            
        #the json object contains input data to the explanation method
        f_explanation, chunks, f_dist = exlainer_controller.explain_factual(self.json_obj)
        if self.args.error == 0:
            # if "stopping" in chunks['ego_action']:
            #     f_explanation = "stopping because my lane is not free"
            # elif "changing lane to the right" in chunks['ego_action']:
            #     f_explanation = "changing lane to the right because my lane is not free" 
            # elif "changing lane to the left" in chunks['ego_action']:
            #     f_explanation = "changing lane to the left because my lane is not free"
            # else:
            #     f_explanation = "moving because my lane is free"

            if "pedestrian" in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('pedestrian', 'a road user')
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "traffic light is green" in chunks['agents_action'][0]:
                #print("##########.... ", chunks['agents_action'][0])
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('traffic light is green', 'there is a traffic sign')
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "traffic light is red" in chunks['agents_action'][0]:
                #print("##########.... ", chunks['agents_action'][0])
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('traffic light is red', 'there is a traffic sign')
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]
            
            else:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('vehicle', get_noised_class('vehicle'))
                idx = chunks['agents_action'][0].find('is')
                f_explanation = chunks['ego_action'] + " because vehicle " + chunks['agents_action'][0][idx:] + " on " + chunks['agents_location'][0]

        elif self.args.error == 1:
            pass

        elif self.args.error == 2:
            if "vehicle" in chunks['agents_action'][0] and "emergency" not in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('vehicle', get_noised_class('vehicle'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]
            
            elif "pedestrian" in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('pedestrian', get_noised_class('pedestrian'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "cyclist" in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('cyclist', get_noised_class('cyclist'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]
            
            elif "motor bike" in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('motor bike', get_noised_class('motor bike'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "emergency vehicle" in chunks['agents_action'][0]:
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('emergency vehicle', get_noised_class('emergency vehicle'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "traffic light is green" in chunks['agents_action'][0]:
                #print("##########.... ", chunks['agents_action'][0])
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('traffic light is green', get_noised_class('traffic light is green'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            elif "traffic light is red" in chunks['agents_action'][0]:
                #print("##########.... ", chunks['agents_action'][0])
                chunks['agents_action'][0] = chunks['agents_action'][0].replace('traffic light is red', get_noised_class('traffic light is red'))
                f_explanation = chunks['ego_action'] + " because " + chunks['agents_action'][0] + " on " + chunks['agents_location'][0]

            # elif "changing lane to the right" in chunks['agents_action']:
            #     f_explanation = "changing lane to the right because my lane is not free"
            # elif "changing lane to the right" in chunks['agents_action']:
            #     f_explanation = "changing lane to the right because my lane is not free"
            # else:
            #     f_explanation = "moving because my lane is free"
            # f_explanation

        self.json_obj[str(self.timestamp)]["f_explanation"] = f_explanation
        self.json_obj[str(self.timestamp)]["f_chunks"] = chunks
        self.json_obj[str(self.timestamp)]["f_dist"] = f_dist
        
       

        print("EXPLANATIONS...", f_explanation)
        if f_explanation != '' and f_explanation != None:
            time_diff = time.time() - self.seconds
            self.json_obj[str(self.timestamp)]['seconds'] = time_diff
            write_log(self.json_obj, filepath='logs/xai_log.json')
            text_to_speech(f_explanation)

        #only readout explanations when:
        # 1. the explanation was actually generated
        # 2. the predicted ego action matches with the ground truth action

        return self.json_obj

    
    def search_lanes_towards_right(self, world, ego_vehicle, actual_actor, current_lane_info):
        """
        This methods scans lane towards the right and returns the lane number of the agent of interest
        """
        
        lane_type = 'Pav'
        num_lane_changes = None
        
        num_lane_changes = 0

        #print("DISTANCE OO", current_lane_info.distance(ego_lane.location))
        
        if current_lane_info != None:
            
            if(str(current_lane_info.lane_type) == 'Driving'):
                basic_agent = BasicAgent(ego_vehicle)
                _, lane_type, distance = basic_agent._vehicle_obstacle_detected(world, ego_vehicle, \
                    [actual_actor], lane_offset=0)
                
                while(True):
                    
                    if current_lane_info != None:
                        if(str(current_lane_info.lane_type) == 'Driving'):
                            
                            num_lane_changes += 1

                            current_lane_info = current_lane_info.get_right_lane()

                        else:
                            break
                    else:
                        break
            else:
                num_lane_changes = -1

        return num_lane_changes, lane_type, distance


    def get_other_agents(self, world, world_snapshot, ego_actor):
        ego_front_transform = get_ego_front_transforms(ego_actor)

        #ego_lane =  _map.get_waypoint(self.ego_actor.get_location())
        dynamic_actors = []
        for actor_snapshot in world_snapshot: # Get the actor and the snapshot information
            actual_actor = world.get_actor(actor_snapshot.id)
            #actual_actor_waypoint =  _map.get_waypoint(actual_actor.get_location())

            #Get the transform of the behind of the vehicle
            target_transform = actual_actor.get_transform()

            if is_within_distance(target_transform, ego_front_transform, 35, [-1, 25]):
                #print("ACTOR TYPE.... ",get_actor_class(actual_actor))
                if get_actor_class(actual_actor) == 'vehicle': # or get_actor_class(actual_actor) == 'walker':
                #actual_actor.type_id.title()[0:7] == 'Vehicle' or actual_actor.type_id.title()[0:6] == 'Walker':

                    if actual_actor.id != ego_actor.id:
                    
                        current_lane_info = self._map.get_waypoint(actual_actor.get_location())

                        num_lane_changes, lane_type, distance = self.search_lanes_towards_right(world, \
                            self.ego_actor, actual_actor, current_lane_info)
                        agent_planner = LocalPlanner(actual_actor)
                        actor_plan = agent_planner.get_incoming_waypoint_and_direction(steps=self.sampling_resolution)[1]
                        
                        nav_index = actor_plan.value
                        if get_speed(actual_actor) < 5:
                            nav_index = 0
                            #print(actor_plan.value)

                        if actor_plan.value < 0:
                            nav_index = 0
                        
                        #print("ACTORRR OOO... ", actual_actor)
                        actor_obj = {
                            "type": get_actor_type(actual_actor),
                            "action": NAVIGATION_ACTIONS[nav_index],
                            "location": [lane_type, num_lane_changes],
                            "dist_from_ego": distance
                        }

                        # if actor_obj["type"] == "EmVehicle":
                        #     actor_obj["type"] = "emergency vehicle"

                        dynamic_actors.append(actor_obj)

                elif get_actor_class(actual_actor) == 'walker':
                    current_lane_info = self._map.get_waypoint(actual_actor.get_location())
                    num_lane_changes, lane_type, distance = self.search_lanes_towards_right(world, \
                            self.ego_actor, actual_actor, current_lane_info)
                    
                    actor_obj = {
                            "type": get_actor_type(actual_actor),
                            "action": 'Mov',
                            "location": [lane_type, num_lane_changes],
                            "dist_from_ego": distance
                        }
                    dynamic_actors.append(actor_obj)
                    
        return dynamic_actors


    def get_tl_object(self, world,  ego_actor):
        ego_front_transform = get_ego_front_transforms(ego_actor)

        #ego_lane =  _map.get_waypoint(self.ego_actor.get_location())
        dynamic_actors = None
        for tl in world.get_actors().filter('traffic.traffic_light*'):
            # Trigger/bounding boxes contain half extent and offset relative to the actor.
            trigger_transform = tl.get_transform()
            #trigger_transform.location += tl.trigger_volume.location
            #trigger_extent = tl.trigger_volume
            #print("TRIGGER EXTENT", trigger_transform)
            #print("EGO TRIGGER EXTENT", ego_front_transform)
            #target_transform = ego_actor.get_transform()
            if is_within_distance(trigger_transform, ego_front_transform, 35, [0, 20]):
                #print("WE GOT HERE...")
                tl_status = "TLMov"
                if str(tl.get_state()).split(".")[-1] != "Green":
                    tl_status = "TLStop"

                actor_obj = {
                    "status": tl_status,
                    "location": "VehLane"
                }
                return actor_obj

        return dynamic_actors

    #def is_overlapping1D(trigger_extent, ):

        #obtain a new route and draw on map
    # def reset_map_route(self, world, _map, ego_origin, ego_destination):
    #     self.global_planner = GlobalRoutePlanner(_map, self.sampling_resolution)
    #     #import app
    #     app.global_route, app.global_route_cmd, app.route_list = self.global_planner.trace_route(ego_origin, ego_destination)
    #     #self.global_route, self.global_route_cmd, self.route_list = self.global_planner.trace_route(ego_origin, ego_destination)
    #     draw_plan_on_map(world, app.global_route, ego_origin, ego_destination)