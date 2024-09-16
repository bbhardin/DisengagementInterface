import numpy as np
from sklearn.tree import DecisionTreeRegressor

import shap
#shap.initjs()
class Condition:
    
    def __init__(self):
        pass
    
    def feature_contribution(self, model, X_test, predicted_output):
        
        explainer_shap = shap.TreeExplainer(model)

        shap_values = explainer_shap.shap_values(X_test)
        #print(shap_values[3])
        #print("****" + str(predicted_output))
        return shap_values[int(predicted_output)][0]
    
    
#     def feature_contribution_imp(self, model, X_test, node_index, values, feature, predicted_output):

#         children_left = model.tree_.children_left
#         children_right = model.tree_.children_right
#         ginis = model.tree_.impurity
#         parent_dic = {}
#         prev_node_id = None
#         importance_data = np.zeros(len(X_test[0]))

#         total_sample = 0
#         dividing_value = 0
#         for i, node_id in enumerate(node_index):
#             # continue to the next node if it is a leaf node
#             if i == 0:
#                 prev_node_id = node_id
#                 yp = 0
#                 yc = values[node_id][0][int(predicted_output[0])]/np.sum(values[node_id])
#                 total_sample = np.sum(values[node_id])

#             left = children_left[node_id]
#             right = children_right[node_id]
#             n_weighted_samples = np.sum(values[node_id])/total_sample
#             l_weighted_samples = np.sum(values[left])/total_sample
#             r_weighted_samples = np.sum(values[right])/total_sample
#             importance_data[feature[node_id]] += (
#                 n_weighted_samples * ginis[node_id] -
#                 l_weighted_samples * ginis[left] -
#                 r_weighted_samples * ginis[right]) * (yc-yp) 

#             prev_node_id = node_id 
#             if i == 0:
#                 dividing_value = n_weighted_samples
#         importance_data /= dividing_value

#         normalizer = np.sum(importance_data)

#         if normalizer > 0.0:
#             # Avoid dividing by zero (e.g., when root is pure)
#             importance_data /= normalizer

#         return importance_data
    
    
    def build_conditions(self, model, X_test, predicted_output):
        leaf_node = model.apply(X_test)
        values = model.tree_.value
        feature = model.tree_.feature
        threshold = model.tree_.threshold
        node_indicator = model.decision_path(X_test)
        # obtain ids of the nodes `sample_id` goes through, i.e., row `sample_id`
        sample_id = 0
        node_index = node_indicator.indices[node_indicator.indptr[sample_id]: \
                                            node_indicator.indptr[sample_id + 1]]

        #save node conditions for root, leaf nodes and full description
        rootnode = np.empty(len(X_test[0]))
        rootnode[:] = np.nan
        leafnode = np.empty(len(X_test[0]))
        leafnode[:] = np.nan
        r_condition = np.zeros(len(X_test[0]))
        l_condition = np.zeros(len(X_test[0]))

        f_dist = []
        for node_id in node_index:
            # continue to the next node if it is a leaf node
            if leaf_node[sample_id] == node_id:
                #this is a leaf node
                f_dist = values[node_id]
                continue

            # check if value of the split feature for sample 0 is below threshold
            if (X_test[sample_id, feature[node_id]] <= threshold[node_id]):
                threshold_sign = "<="
                if np.isnan(rootnode[feature[node_id]]):
                    rootnode[feature[node_id]] = threshold[node_id]
                    r_condition[feature[node_id]] = 0
                else:
                    leafnode[feature[node_id]] = threshold[node_id]
                    l_condition[feature[node_id]] = 0

            else:
                threshold_sign = ">"
                if np.isnan(rootnode[feature[node_id]]):
                    rootnode[feature[node_id]] = threshold[node_id]
                    r_condition[feature[node_id]] = 1
                else:
                    leafnode[feature[node_id]] = threshold[node_id]
                    l_condition[feature[node_id]] = 1
        
        #importance_data = self.feature_contribution(model, X_test, node_index, values, feature, predicted_output)
        importance_data = self.feature_contribution(model, X_test, predicted_output)
#         importance_data2 = self.feature_contribution_imp(model, X_test, node_index, values, feature, predicted_output)
#         print(importance_data)
#         print(importance_data2)
        return (rootnode, leafnode, r_condition, l_condition), importance_data, f_dist
    
    
    def build_conditions_cf(self, model, X_test, predicted_output, constraints):
        
        leaf_node = model.apply(X_test)
        values = model.tree_.value
        feature = model.tree_.feature
        threshold = model.tree_.threshold
        node_indicator = model.decision_path(X_test)
        children_left = model.tree_.children_left
        children_right = model.tree_.children_right
        # obtain ids of the nodes `sample_id` goes through, i.e., row `sample_id`
        sample_id = 0
        node_index = node_indicator.indices[node_indicator.indptr[sample_id]: \
                                            node_indicator.indptr[sample_id + 1]]

        #save node conditions for root, leaf nodes and full description
        rootnode = np.empty(len(X_test[0]))
        rootnode[:] = np.nan
        leafnode = np.empty(len(X_test[0]))
        leafnode[:] = np.nan
        r_condition = np.zeros(len(X_test[0]))
        l_condition = np.zeros(len(X_test[0]))

        penultimate = len(node_index) - 2 #index of critical node
        #Get nodes for counterfactuals
   
        node_index = self.get_counterfactual(model, X_test, penultimate, node_index, predicted_output, constraints)
        cf_output = ''
        
        #used to reverse the condition of the c
        critical_node_f = 0
        cf_dist = []
        for i, node_id in enumerate(node_index):
            # continue to the next node if it is a leaf node
            if  node_id == node_index[-1]:
                #this is a leaf node, so check prediction
                cf_output = np.argmax(values[node_id])
                cf_dist = values[node_id]
                #print(values[node_id])
                break

            # check if value of the split feature for sample 0 is below threshold
            if (X_test[sample_id, feature[node_id]] <= threshold[node_id]):

                threshold_sign = "<="
                if np.isnan(rootnode[feature[node_id]]):
                    rootnode[feature[node_id]] = threshold[node_id]
                    if children_left[node_id] == node_index[i+1]:
                        r_condition[feature[node_id]] = 0
                    else:
                        r_condition[feature[node_id]] = 1
                else:
                    leafnode[feature[node_id]] = threshold[node_id]
                    if children_left[node_id] == node_index[i+1]:
                        l_condition[feature[node_id]] = 0
                    else:
                        l_condition[feature[node_id]] = 1

            else:
                threshold_sign = ">"
                if np.isnan(rootnode[feature[node_id]]):
                    rootnode[feature[node_id]] = threshold[node_id]
                    if children_left[node_id] == node_index[i+1]:
                        r_condition[feature[node_id]] = 0
                    else:
                        r_condition[feature[node_id]] = 1
                else:
                    leafnode[feature[node_id]] = threshold[node_id]
                    if children_left[node_id] == node_index[i+1]:
                        l_condition[feature[node_id]] = 0
                    else:
                        l_condition[feature[node_id]] = 1
           
        return (rootnode, leafnode, r_condition, l_condition, cf_output, critical_node_f), cf_dist
    
    
    # Function to perform level order traversal 
    # until we find the first leaf node 
    def get_counterfactual(self, model, X_test, node, node_index, predicted_class, constraints): 

        # Using those arrays, we can parse the tree structure:
        if int(X_test[0][4]) > 3:
            target = 1
        else:
            target = X_test[0][4]
        n_nodes = model.tree_.node_count
        children_left = model.tree_.children_left
        children_right = model.tree_.children_right
        feature = model.tree_.feature
        threshold = model.tree_.threshold
        values = model.tree_.value

        # The tree structure can be traversed to compute various properties such
        # as the depth of each node and whether or not it is a leaf.
        node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
        is_leaves = np.zeros(shape=n_nodes, dtype=bool)

        visited = np.zeros(len(values), dtype=bool)
        found = False
        while found == False:
            
            parent_dic = {}
            if node == -1:
                return []
            parent_dic[node_index[node]] = node_index[node]

            stack = [(node_index[node], -1)]  # seed is the root node id and its parent depth
            while len(stack) > 0:
                node_id, parent_depth = stack.pop(0)
                node_depth[node_id] = parent_depth + 1
                visited[node_id] = True

                # If we have a test node
                if (children_left[node_id] != children_right[node_id]):

                    if visited[children_right[node_id]] != True:
                        
                        if feature[node_id] in constraints:
                            idx = feature[node_id]
                            if X_test[0][idx] > threshold[node_id]:
                                stack.append((children_right[node_id], parent_depth + 1))
                                parent_dic[children_right[node_id]] = node_id
                        else:
#                             idx = feature[children_right[node_id]]
#                             if threshold[children_right[node_id]] <= X_test[0][idx] + 30 and threshold[children_right[node_id]] >= X_test[0][idx] - 30: 
                            stack.append((children_right[node_id], parent_depth + 1))
                            parent_dic[children_right[node_id]] = node_id
                                
                    if visited[children_left[node_id]] != True:
                        if feature[node_id] in constraints:
                            idx = feature[node_id]
                            if X_test[0][idx] <= threshold[node_id]:
                                stack.append((children_left[node_id], parent_depth + 1))
                                parent_dic[children_left[node_id]] = node_id
                        else:
#                             idx = feature[children_left[node_id]]
#                             if threshold[children_left[node_id]] <= X_test[0][idx] + 30 and threshold[children_left[node_id]] > X_test[0][idx] - 30: 
                            stack.append((children_left[node_id], parent_depth + 1))
                            parent_dic[children_left[node_id]] = node_id
                            
                                
                else:
                    
                    if (type(model) == DecisionTreeRegressor):
                        if target != None:
                            if (target[1] == -1 and values[node_id] < target[0]):
                                found = True
                                break
                            elif (target[1] == 1 and values[node_id] > target[0]):
                                found = True
                                break
                        else:
                            # check to avoid printing the original prediction leaf id as counterfactual
                            if(node_id != node_index[-1]):
                                found = True
                                break
                                
                    elif (type(model) != DecisionTreeRegressor):
                        if target != None:
                            if(target == np.argmax(values[node_id])):
                                found = True
                                break
                        else:
                            if(predicted_class != np.argmax(values[node_id])):
                                found = True
                                break

            if found == False:
                node = node - 1                

        node_output = self.print_path(node_id, parent_dic)

        return node_output
    
    def print_path(self, data, parent): 

        node_output = []

        while (parent[data] != data):

            node_output = [data] + node_output
            data = parent[data]

        node_output = [parent[data]] + node_output

        return node_output