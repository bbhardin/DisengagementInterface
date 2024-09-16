from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier #
from sklearn.ensemble import RandomForestRegressor #
from operator import itemgetter
import numpy as np

from commentary.condition import Condition
from commentary.language import Language

#The Explainer class checks the type of tree to be explained, call the appropriate 
# tree conditiion building procedure and uses the Language class to generate the
# appropriate explanation (i.e why and what-if)
#The Explainer class checks the type of tree to be explained, call the appropriate 
# tree conditiion building procedure and uses the Language class to generate the
# appropriate explanation (i.e why and what-if)


class ExplainerService(object):    
    #This function is first called to generate an explanation
    
    def __init__(self):
        pass
    
    def factual(self, model, X_test, col_names, output_category):
        
        #Check the type of model that have been passed and process accordingly
        #if decision tree regressor model, build a collections of conditions in the nodes
        #both for factual and counterfactual
        condition = Condition()
        language = Language()
        tartget = X_test[0][4]
        f_dist = []
        cf_dist = []
        if type(model) == DecisionTreeRegressor:
            predicted_output = model.predict(X_test)
            tree_details, importance_data, f_dist = condition.build_conditions(model, X_test, predicted_output)

        elif type(model) == DecisionTreeClassifier:
            predicted_output = np.argmax(model.predict_proba(X_test))
            tree_details, importance_data, f_dist = condition.build_conditions(model, X_test, predicted_output)
            
        elif type(model) == RandomForestRegressor:
            final_tree = 0
            pred_values = []
            predicted_output = model.predict(X_test)
            model = self.get_regressor_tree(model, X_test)
            tree_details, importance_data, f_dist = condition.build_conditions(model, X_test, predicted_output)
            
        elif type(model) == RandomForestClassifier:
            predicted_output = model.predict(X_test)
            #print(predicted_output)
            model = self.get_classification_tree(model, X_test, predicted_output)
            tree_details, importance_data, f_dist = condition.build_conditions(model, X_test, predicted_output)
                        
        
        exp_str, chunks = language.generate_why(model, tree_details, col_names, output_category, predicted_output, X_test, importance_data)
        #print(constraints)
        return exp_str, chunks, f_dist[0].tolist()


    def counterfactual(self, model, X_test, col_names, output_category, constraints=None):
        
        #Check the type of model that have been passed and process accordingly
        #if decision tree regressor model, build a collections of conditions in the nodes
        #both for factual and counterfactual
        condition = Condition()
        language = Language()
        tartget = X_test[0][4]
        f_dist = []
        cf_dist = []

        if type(model) == DecisionTreeRegressor:
            predicted_output = model.predict(X_test)
            tree_details_cf, cf_dist = condition.build_conditions_cf(model, X_test, predicted_output, constraints)

        elif type(model) == DecisionTreeClassifier:
            predicted_output = np.argmax(model.predict_proba(X_test))
            tree_details_cf, cf_dist = condition.build_conditions_cf(model, X_test, predicted_output, constraints)

        elif type(model) == RandomForestRegressor:
            final_tree = 0
            pred_values = []
            predicted_output = model.predict(X_test)
            model = self.get_regressor_tree(model, X_test)
            tree_details_cf, cf_dist = condition.build_conditions_cf(model, X_test, predicted_output, constraints)

        elif type(model) == RandomForestClassifier:
            predicted_output = model.predict(X_test)
            #print(predicted_output)
            model = self.get_classification_tree(model, X_test, predicted_output)
            tree_details_cf, cf_dist = condition.build_conditions_cf(model, X_test, predicted_output, constraints)
            
        #Predicted_output is either a continuous value or a class id for regression \
        # or classification task respectively
            
        cf_exp_str = 'NULL'
        pred_class = tree_details_cf[4]
        cf_exp_str, chunks = language.generate_what_if(model, tree_details_cf, X_test, col_names, output_category, constraints)
        
            
        return cf_exp_str, chunks, cf_dist

    
    def get_regressor_tree(self, model, X_test):
        pred_values = []
        for i, estimator in enumerate(model.estimators_):
            leaf_node = estimator.apply(X_test)
            values = estimator.tree_.value
            sample_id = 0
            #predicted value within this function
            leaf_id = leaf_node[sample_id]

            #decision path leaf node class
            pred_values.append((i, values[leaf_id]))

        #Get the median of the the sorted list of tuples by predicted values
        pred_values_sorted = sorted(pred_values, key=itemgetter(1))
        if len(pred_values_sorted) % 2 == 0:
            idx = int(len(pred_values_sorted)/2) - 1
            m = np.mean([pred_values_sorted[idx][1], pred_values_sorted[idx+1][1]])
        
            if m - pred_values_sorted[idx][1] > pred_values_sorted[idx+1][1] - m:
                tree_index = idx+1
            else:
                tree_index = idx
        else:
            tree_index = int(len(pred_values_sorted)/2)
        final_tree = pred_values_sorted[tree_index][0]
        
        tree = model.estimators_[final_tree]
        return tree
        

    def get_classification_tree(self, model, X_test, predicted_output):
        
        max_sample = 0
        final_tree = 0
        row = 0
        scores = np.zeros((1, (X_test.shape[1] + 1)))
        feature_map = []
        for i, estimator in enumerate(model.estimators_):
            
            sample_id = 0
            leaf_node = estimator.apply(X_test)
            values = estimator.tree_.value
            #predicted value within this function
            leaf_id = leaf_node[sample_id]
            #decision path leaf node class
            class_id = np.argmax(values[leaf_id])
            
            if class_id == predicted_output:
                            
                node_indicator = estimator.decision_path(X_test)
                node_index = node_indicator.indices[node_indicator.indptr[sample_id]: \
                                            node_indicator.indptr[sample_id + 1]]
        
                features = estimator.tree_.feature
                #print(values[node_index[-1]][0][predicted_output])
                conf = values[node_index[-1]][0][int(predicted_output[0])]
                feature_map.append((features[node_index[0:-1]], conf, i))
               
                #frequency count for feeatures
                scores[0, features[node_index[0:-1]]] = scores[0, features[node_index[0:-1]]] + 1
                
                row = row + 1
                #matrix = np.vstack((matrix, tmp_mat))
#                 if values[leaf_id][sample_id][class_id] > max_sample:
#                     max_sample = values[leaf_id][sample_id][class_id]
#                     final_tree = i
                
       
        final_scores = []
        for i in range(row):
            importance = 0
            
            for j in set(feature_map[i][0]):
                if scores[0,j] > 1:
                    importance = importance + scores[0,j]
        
            final_scores.append((feature_map[i][2], importance, feature_map[i][1]))
        
        final_scores = sorted(final_scores, key=itemgetter(1,2), reverse=True)
        #print(final_scores)
        final_tree = final_scores[0][0]
        tree = model.estimators_[final_tree]
        #printprint(final_scores)
        return tree