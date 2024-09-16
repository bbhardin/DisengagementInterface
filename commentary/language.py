import numpy as np
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier #
from sklearn.ensemble import RandomForestRegressor #


CONV_DICT_LANG = {'20': 'cyclist is waiting', 
                 '50': 'cyclist is crossing', '80':'vehicle is crossing', '110':'pedestrain is crossing', 
                  '140':'pedestrian is not crossing', '160':'pedestrian is moving', '190':'traffic light is green',
                  '210':'traffic light is red', '240':'vehicle is moving', '270':'traffic congestion',
                  '300':'vehicle stopped', '330':'cyclist is moving', '350':'cyclist stopped', 
                  '380':'motor bike is braking', '400':'motor bike is moving', '420':'motor bike stopped',
                '450':'vehicle is braking', '470':'there is a vehicle with hazard lights'
            }
CONV_DICT_LANG_CF = {'20':'road is free', 
                  '50':'road is free', '80':'road is free', '110':'pedestrain is crossing', 
                  '140':'road is free', '160':'road is free', '190':'the traffic light is green',
                 '210': 'the traffic light is red', '240':'road is free', '270':'traffic congestion',
                  '300':'a vehicle stopped', '330':'road is free', '350':'cyclist stopped', 
                  '380':'a motor bike is braking', '400':'road is free', '420':'motor bike stopped',
                  '450':'a vehicle is braking', '470':'there is a vehicle with hazard lights'
            }
AV_GLOBAL_PLAN = ['stop', 'move', 'move to the right lane', 'move to the left lane', 'turn right', 'turn left',
                    'overtake']

class Language():
    
    def __init__(self, select='best'):
        self.select = select


    def check_agent(self, bound, inequality, feature, cf = False):
        
        agent_action = []
        
        lang_dict = None
        #print(str(bound) + ' ' + str(inequality))
        
        if cf == True:
            lang_dict = CONV_DICT_LANG_CF.copy()
        else:
            lang_dict = CONV_DICT_LANG.copy()

        if len(bound) < 2:
            
            if inequality == 0:
                i = 0
                for key, value in lang_dict.items():
                    key1 = int(key)
                    if i == 0 and bound[0] < 15:
                        agent_action = 'ego\'s lane is free'
                        break
                    
                    elif i == 0 and key1 > bound[0]:
                        agent_action = value
                        break
                    elif key1 < bound[0]:
                        agent_action = value
                    else:
                        break
                    i += 1
                        
            else:
                for key, value in lang_dict.items():
                    key1 = int(key)
                    if key1 >= bound[0]:
                        #print(value)
                        agent_action = value
                        break
                #agent_action = find_range(bound)
        else:
            for key, value in lang_dict.items():
                key1 = int(key)
                if (key1 >= bound[0] and key1 <= bound[1]) or (key1 >= bound[1] and key1 <= bound[0]):
                    #print(str(value) +' within ...'+ feature+ ' b ' + str(bound))
                    agent_action = value

        agent_action = [str(agent_action), feature]

        return agent_action
        
    def generate_why(self, model, tree_details, col_names, output_category, predicted_output, X_test, importance_data):
        #fetch returned lists
        rootnode = tree_details[0]
        leafnode = tree_details[1]
        r_condition = tree_details[2]
        l_condition = tree_details[3]

        #process returned list to return causes
        causes = []
        sign = ''
        for i in range(len(rootnode)):
            if np.isnan(rootnode[i]):
                continue
            elif np.isnan(rootnode[i]) == False  and  np.isnan(leafnode[i]):
                sign = ''
                if r_condition[i] == 0:
                    agent_exp = self.check_agent([rootnode[i]], r_condition[i], col_names[i])               
                    causes.append(agent_exp)

                else:
                    agent_exp = self.check_agent([rootnode[i]], r_condition[i], col_names[i])
                    causes.append(agent_exp)

            elif np.isnan(rootnode[i]) == False and np.isnan(leafnode[i]) == False:
                if (rootnode[i] > leafnode[i] and l_condition[i] == 0):
                    agent_exp = self.check_agent([leafnode[i]], l_condition[i], col_names[i])
                    causes.append(agent_exp)
                    
                elif (rootnode[i] > leafnode[i] and l_condition[i] == 1):
                    agent_exp = self.check_agent([leafnode[i], rootnode[i]], l_condition[i], col_names[i])
                    causes.append(agent_exp)

                elif (rootnode[i] < leafnode[i] and l_condition[i] == 1):
                    agent_exp = self.check_agent([leafnode[i]], l_condition[i], col_names[i])
                    causes.append(agent_exp)

                elif (rootnode[i] < leafnode[i] and l_condition[i] == 0):
                    agent_exp = self.check_agent([leafnode[i], rootnode[i]], l_condition[i], col_names[i])
                    causes.append(agent_exp)

        exp = ""
        
        #Get sorted feature importance list
        best_features = []
        
        max_imp = np.max(importance_data)

        for index, imp in enumerate(importance_data):
            if col_names[index] != 'my plan' and X_test[0][index] < 1:
                continue
            else:
                
                if imp > 0:
                    if imp/max_imp > 0.5:
                        action = ''
                        for key, value in CONV_DICT_LANG.items():
                            if X_test[0][index] == int(key):
                                best_features.append([value, col_names[index]])
                                
        
        exp_chunks = {"ego_action": "", "agents_action": [],
            "agents_location": []
        }
            
        for c in range(len(best_features)):
            
            if c < len(best_features)-1:
                if best_features[c][1] == 'traffic light':    
                    exp = exp + best_features[c][0]  + ' on my lane, '
                    exp_chunks["agents_action"].append(best_features[c][0])
                    exp_chunks["agents_location"].append("my lane")
                else:
                    exp = exp + best_features[c][0]  + ' on ' + best_features[c][1] + ', '
                    exp_chunks["agents_action"].append(best_features[c][0])
                    exp_chunks["agents_location"].append(best_features[c][1])
                
            elif c >= len(best_features)-1:
                if best_features[c][1] == 'traffic light':    
                    exp = exp + best_features[c][0]  + ' on my lane.'
                    exp_chunks["agents_action"].append(best_features[c][0])
                    exp_chunks["agents_location"].append("my lane")
                else:
                    exp = exp + best_features[c][0]  + ' on ' + best_features[c][1] + '.'
                    exp_chunks["agents_action"].append(best_features[c][0])
                    exp_chunks["agents_location"].append(best_features[c][1])
                

        if type(model) == RandomForestClassifier or type(model) == DecisionTreeClassifier:
            exp_chunks["ego_action"] = output_category[int(predicted_output)]
            exp = output_category[int(predicted_output)] + \
                            ' because ' + exp
        
        if len(best_features) == 0:
            exp = ""
        
        return exp, exp_chunks

        
    def generate_what_if(self, model, tree_details, X_test, col_names, output_category, constraints):
        #fetch returned lists
        rootnode = tree_details[0]
        leafnode = tree_details[1]
        r_condition = tree_details[2]
        l_condition = tree_details[3]

        #process returned list to return causes
        causes = []

        for i in range(len(rootnode)):

            if np.isnan(rootnode[i]):
                continue
            elif np.isnan(rootnode[i]) == False  and  np.isnan(leafnode[i]):
                sign = ''
                if r_condition[i] == 0:
                    agent_exp = self.check_agent([rootnode[i]], r_condition[i], col_names[i], True)
                    causes.append(agent_exp)
                else:
                    agent_exp = self.check_agent([rootnode[i]], r_condition[i], col_names[i], True)
                    causes.append(agent_exp)
            elif np.isnan(rootnode[i]) == False and np.isnan(leafnode[i]) == False:
                if (rootnode[i] > leafnode[i] and l_condition[i] == 0):
                    agent_exp = self.check_agent([leafnode[i]], l_condition[i], col_names[i], True)
                    causes.append(agent_exp)
                elif (rootnode[i] > leafnode[i] and l_condition[i] == 1):
                    agent_exp = self.check_agent([leafnode[i], rootnode[i]], l_condition[i], col_names[i], True)
                    causes.append(agent_exp)
                elif (rootnode[i] < leafnode[i] and l_condition[i] == 1):
                    agent_exp = self.check_agent([leafnode[i]], l_condition[i], col_names[i], True)
                    causes.append(agent_exp)
                elif (rootnode[i] < leafnode[i] and l_condition[i] == 0):
                    agent_exp = self.check_agent([leafnode[i], rootnode[i]], l_condition[i], col_names[i], True)
                    causes.append(agent_exp)

        #Generate explanation
        exp = ""
        exp_chunks = {"ego_action": "", "agents_action": [],
            "agents_location": []
            }
        if type(model) == RandomForestClassifier or type(model) == DecisionTreeClassifier:
            exp_chunks["ego_action"] = self.av_global_plan[int(X_test[0][4])]
            exp = 'For us to be able to ' + self.av_global_plan[int(X_test[0][4])] + ', the following should be happening: '

        col_names2 = np.array(col_names) 
        for c in range(len(causes)):
            if causes[c][1] not in col_names2[constraints]: 
                if c < len(causes)-1:
                    
                    if causes[c][1] == 'traffic light':    
                        exp = exp + causes[c][0]  + ' on my lane; '
                        exp_chunks["agents_action"].append(causes[c][0])
                        exp_chunks["agents_location"].append("my lane")
                    else:
                        exp = exp + causes[c][0]  + ' on ' + causes[c][1] + '; '
                        exp_chunks["agents_action"].append(causes[c][0])
                        exp_chunks["agents_location"].append(causes[c][1])
                else:
                    exp = exp + causes[c][0]  + ' on ' + causes[c][1] + '.'
                    exp_chunks["agents_action"].append(causes[c][0])
                    exp_chunks["agents_location"].append(causes[c][1])
                    
        if len(causes) == 0:
            exp = ""
            
        return exp, exp_chunks