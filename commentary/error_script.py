dynamic_labels = ['cyclist', 'bus', 'pedestrian', 'motor bike', 'emergency vehicle', 'van', 'vehicle']
dynamic_weights = [[0.885, 0, 0.115, 0, 0, 0, 0],
    [0, 0.96, 0, 0, 0.03, 0.01, 0], 
    [0.007, 0, 0.988, 0.005, 0, 0, 0], 
    [0.067, 0, 0.012, 0.921, 0, 0, 0], 
    [0, 0.023, 0, 0, 0.971, 0.006, 0],
    [0, 0.056, 0, 0, 0.014, 0.93, 0], 
    [0, 0, 0.004, 0, 0.002, 0.066, 0.928]] #


static_labels = ['traffic light is red', 'traffic light is green', 'unknown']
static_weights = [[0.98, 0.01, 0.01], 
    [0.12, 0.88, 0], 
    [0.11, 0.04, 0.85]]

def get_noised_class(label):

    if 'traffic light' in label:
        weight_d = static_weights[static_labels.index(label)]

        weight_d2 = set(weight_d)
    
        # Removing the largest element from temp list
        weight_d2.remove(max(weight_d2))
        second_largest = max(weight_d2)
        noised_label = static_labels[weight_d.index(second_largest)]
        #print("*****************.... ", noised_label)
        return noised_label

    else:

        weight_d = dynamic_weights[dynamic_labels.index(label)]

        weight_d2 = set(weight_d)
    
        # Removing the largest element from temp list
        weight_d2.remove(max(weight_d2))
        second_largest = max(weight_d2)
        noised_label = dynamic_labels[weight_d.index(second_largest)]
        return noised_label
