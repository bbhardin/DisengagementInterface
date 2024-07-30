import pickle

import numpy as np
from agents.navigation.local_planner import RoadOption

from commentary.explainer_service import ExplainerService
from commentary.language import CONV_DICT_LANG


NAVIGATION_PLAN_CODES = {
            "VOID": 0,
            "STOP": 0,
            "LANEFOLLOW": 1,
            "STRAIGHT": 1,
            "CHANGELANERIGHT": 2,
            "CHANGELANELEFT": 3,
            "RIGHT": 4,
            "LEFT": 5
        }

ENCODINGS = {'CyclistWait2X':20, 'PedestrianWait2X':20, 'CyclistXingFmRht':50,'CyclistXingFmLft':50, 'VehicleXingFmLft':80, 'PedestrianCross':110, 
                    'PedestrianXingFmLft':110, 'PedestrianXingFmRht':110, 'PedestrianStop':140, 'PedestrianMov':160, 'TLMov':190, 'TLStop':210,
                    'VehicleMov':240, 'EmVehicleMov': 240, 'TrafficCongestion': 270, 'VehicleStop': 300, 'EmVehicleStop': 300,
                    'CyclistMov':330, 'CyclistStop':350, 'MotorBikeBrake': 380, 'MotorBikeMov':400, 'MotorBikeStop':420, 'VehicleBrake': 450,
                    'VehicleBrakeMov': 450, 'VehicleMovBrake': 450, 'VehicleStopHazlit': 470, 'VehicleMovHazlit': 470, 'MotorBike': 400
                    }

class ExplainerController(object):
    """
    This class unpacks the json object provided as input, preprocesses it and calls the explainer service where 
    the explanation generation logic is defined.
    """
    def __init__(self, file_path, args):
        with open(file_path, 'rb') as file:  
            self.model = pickle.load(file)

        self.f_output_category = ['stopping', 'moving', 'changing lane to the right', 
                   'changing lane to the left']

        self.cf_output_category = ['is stopping', 'is moving', 'is changing lane to the right', 
                   'is changing lane to the left']
        self.args = args
                   
        #y_test = data4eval['EgoAction']
        #y_pred = clf.predict(np.array(X_test_new))
        

    def get_model_payload(self, json_obj):
        #json_obj = dict(json_obj)
        id = list(json_obj.keys())
        id = str(id[0])
        #print(json_obj[id])
        other_actor_list = json_obj[id]['other_actors']
        real_actors = {
            "VehLane": {
                "dist": 100000,
                "type": "",
                "action": ""
                },
            "OutgoLane": {
                "dist": 100000,
                "type": "",
                "action": ""
                },
            "IncomLane": {
                "dist": 100000,
                "type": "",
                "action": ""
            }
        }
        
        payload = [[0,0,0,0,0]]
        if len(other_actor_list) > 0:

            for actor in other_actor_list:
                if actor['location'][0] == "VehLane":
                    #payload.append(discretise(actor['type']))
                    if real_actors['VehLane']["dist"] > actor['dist_from_ego']:
                        real_actors['VehLane']["dist"] = actor['dist_from_ego']
                        real_actors['VehLane']["type"] = actor["type"]
                        real_actors['VehLane']["action"] = actor["action"]
                        payload[0][0] = ENCODINGS[real_actors["VehLane"]["type"] + real_actors["VehLane"]["action"]]
                            
                elif actor['location'][0] == "OutgoLane":
                    if real_actors['OutgoLane']["dist"] > actor['dist_from_ego']:
                        real_actors['OutgoLane']["dist"] = actor['dist_from_ego']
                        real_actors['OutgoLane']["type"] = actor["type"]
                        real_actors['OutgoLane']["action"] = actor["action"]
                        payload[0][2] = ENCODINGS[real_actors["OutgoLane"]["type"] + real_actors["OutgoLane"]["action"]]
                
                elif actor['location'][0] == "IncomLane":
                    if real_actors['IncomLane']["dist"] > actor['dist_from_ego']:
                        real_actors['IncomLane']["dist"] = actor['dist_from_ego']
                        real_actors['IncomLane']["type"] = actor["type"]
                        real_actors['IncomLane']["action"] = actor["action"]
                        payload[0][1] = ENCODINGS[real_actors["IncomLane"]["type"] + real_actors["IncomLane"]["action"]]
            
            
        if json_obj[id]["ego_related_traffic_light"] != None:
            payload[0][3] = ENCODINGS[json_obj[id]["ego_related_traffic_light"]["status"]]
        
        #print(json_obj[id])
        payload[0][4] = NAVIGATION_PLAN_CODES[json_obj[id]["ego_plan"]]
        payload = np.array(payload)
        
        return payload, real_actors

    
    def explain_factual(self, json_obj):
        payload, real_actors = self.get_model_payload(json_obj)
        
        #names of fields in input dataset
        col_names = ["my lane", "incoming lane", "outgoing lane", "traffic light", "our plan"]
        # output_category = ['is stopping', 'is moving', 'is changing lange to the right', 
        #            'is changing lane to the left']

        explainer_service = ExplainerService()
        id = list(json_obj.keys())
        id = str(id[0])
        f_expl, exp_chunks, f_dist = explainer_service.factual(self.model, payload, col_names, self.f_output_category)
        #print("EGO ACTION..." + str(json_obj[id]["ego_action"]) + " Predicted action..: " + str(exp_chunks["ego_action"]))

        if real_actors['VehLane']['type'] == "EmVehicle":
            if "my lane" in f_expl:
                f_expl = f_expl.replace('vehicle', 'emergency vehicle')
                exp_chunks['agents_action'][0] = exp_chunks['agents_action'][0].replace('vehicle', 'emergency vehicle')

        if real_actors['IncomLane']['type'] == "EmVehicle":
            if "incoming lane" in f_expl:
                f_expl = f_expl.replace('vehicle', 'emergency vehicle')
                exp_chunks['agents_action'][0] = exp_chunks['agents_action'][0].replace('vehicle', 'emergency vehicle')
        
        if real_actors['OutgoLane']['type'] == "EmVehicle":
            if "outgoing lane" in f_expl:
                f_expl = f_expl.replace('vehicle', 'emergency vehicle')
                exp_chunks['agents_action'][0] = exp_chunks['agents_action'][0].replace('vehicle', 'emergency vehicle')


        if self.args.dualmode == "false":
            if NAVIGATION_PLAN_CODES[json_obj[id]["ego_action"]] != \
                self.f_output_category.index(exp_chunks["ego_action"]):
                f_expl = ""
                exp_chunks = {"ego_action": "", "agents_action": [],
                                "agents_location": []
                    }
                f_dist = []

        else:
            try: 
                if f_expl == "" or NAVIGATION_PLAN_CODES[json_obj[id]["ego_action"]] != \
                    self.f_output_category.index(exp_chunks["ego_action"]):
                    
                    f_expl, exp_chunks, f_dist = self.generate_f_using_ground_truth(json_obj, payload, real_actors)

                
            except:
                pass

        return f_expl, exp_chunks, f_dist


    def explain_counterfactual(self, json_obj):
        payload = self.get_model_payload(json_obj)

        #names of fields in input dataset
        col_names = ["my lane'", "incoming lane", "outgoing lane", "traffic light", "our plan"]
        
        #constraints are specific to the counterfactual explanation generation process. Restrictions on the 
        #type of explanations not to generate are specified.
        constraints = []
        for i, x in enumerate(payload[0]):
            if x < 1 and i != 4:
                constraints.append(i)
        constraints.append(4)

        explainer_service = ExplainerService()
        cf_expl, chunks, f_dist = explainer_service.counterfactual(self.model, payload, col_names, self.cf_output_category, constraints)
        return cf_expl, chunks, f_dist


    def generate_f_using_ground_truth(self, json_obj, payload, real_actors):
        exp_chunks = {"ego_action": "", "agents_action": [],
                            "agents_location": []
                        }
        f_expl = ""
        id = list(json_obj.keys())
        id = str(id[0])
        if json_obj[id]["ego_action"] == "STOP":
            exp_chunks["ego_action"] = "stopping"
            if payload[0][3] == 210:
                f_expl = "stopping because traffic light is red on my lane"
                exp_chunks["agents_action"].append("traffic light is red")
                exp_chunks["agents_location"].append("my lane")
            elif payload[0][0] != 0:
                act_exp = None
                if real_actors['VehLane']['type'] == "EmVehicle":
                    act_exp = CONV_DICT_LANG[str(payload[0][0])].replace('vehicle', 'emergency vehicle')
                else:
                    act_exp = CONV_DICT_LANG[str(payload[0][0])]
                f_expl = "stopping because " + act_exp + " on my lane"
                exp_chunks["agents_action"].append(act_exp)    
                exp_chunks["agents_location"].append("my lane")
            else:
                f_expl = "stopping because my lane is not free"
                exp_chunks["agents_action"].append("my lane is not free")

        
        elif json_obj[id]["ego_action"] == RoadOption.LANEFOLLOW.name:
            exp_chunks["ego_action"] = "moving"
            #print(payload)
            if payload[0][0] != 0:
                act_exp = None
                if real_actors['VehLane']['type'] == "EmVehicle":
                    act_exp = CONV_DICT_LANG[str(payload[0][0])].replace('vehicle', 'emergency vehicle')
                else:
                    act_exp = CONV_DICT_LANG[str(payload[0][0])]
                f_expl = "moving because " + act_exp + " on my lane"
                exp_chunks["agents_action"].append(act_exp)
                exp_chunks["agents_location"].append("my lane")

            elif payload[0][3] == 190:
                f_expl = "moving because traffic light is green on my lane"
                exp_chunks["agents_action"].append("traffic light is green")
                exp_chunks["agents_location"].append("my lane")
            
            else:
                f_expl = "moving because my lane is free"
                exp_chunks["agents_action"].append("my lane is free")

        elif json_obj[id]["ego_action"] == RoadOption.CHANGELANELEFT.name:
            exp_chunks["ego_action"] = "changing lane to the left"
            if payload[0][0] != 0:
                act_exp = None
                if real_actors['VehLane']['type'] == "EmVehicle":
                    act_exp = CONV_DICT_LANG[str(payload[0][0])].replace('vehicle', 'emergency vehicle')
                else:
                    act_exp = CONV_DICT_LANG[str(payload[0][0])]
                f_expl = "changing lane to the left because " + act_exp + " on my lane"
                exp_chunks["agents_action"].append(act_exp)
                exp_chunks["agents_location"].append("my lane")
                
            else:
                f_expl = "changing lane to the left because left lane is free"
                exp_chunks["agents_action"].append("left lane is free")

        elif json_obj[id]["ego_action"] == RoadOption.CHANGELANERIGHT.name:
            exp_chunks["ego_action"] = "changing lane to the right"
            if payload[0][0] != 0:
                act_exp = None
                if real_actors['VehLane']['type'] == "EmVehicle":
                    act_exp = CONV_DICT_LANG[str(payload[0][0])].replace('vehicle', 'emergency vehicle')
                else:
                    act_exp = CONV_DICT_LANG[str(payload[0][0])]
                f_expl = "changing lane to the right because " + act_exp + " on my lane"

                exp_chunks["agents_action"].append(act_exp)
                exp_chunks["agents_location"].append("my lane")
            else:
                f_expl = "changing lane to the right because right lane is free"
                exp_chunks["agents_action"].append("right lane is free")

        f_dist = []
        return f_expl, exp_chunks, f_dist