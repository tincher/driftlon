def get_data_for_keys(common_keys, X):
    values_list = []
    for key in common_keys:
        values = [element[key] for element in X]
        values_list.append(values)
    return values_list

def get_all_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: any(x in element.keys() for element in X), keys)))
    return result_keys
