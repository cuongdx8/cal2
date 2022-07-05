def remove_empty_or_none(data: dict):
    result = {}
    for key in data.keys():
        if data[key]:
            result[key] = data[key]
    return result
