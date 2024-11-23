from bson import ObjectId


def objectid_to_str(data):
    """Recursively convert all ObjectId fields in the data to strings."""
    if isinstance(data, dict):
        return {key: objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data
