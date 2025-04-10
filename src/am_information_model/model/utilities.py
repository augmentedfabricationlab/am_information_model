
__all__ = [
    "_serialize_to_data",
    "_deserialize_from_data"
]

def _serialize_to_data(obj):
    if obj is not None:
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, "__data__"):
            return obj.__data__
        else:
            raise AttributeError(f"Object {obj} does not have 'data' attribute.")
    else:
        return None


def _deserialize_from_data(data):
    if data is not None and data.get('dtype') is not None:
        module, attr = data.get('dtype').split('/')
        cls = globals().get(attr)
        if cls is None:
            cls = getattr(__import__(module, fromlist=[attr]), attr)
        return cls.from_data(data.get('data'))
    else:
        return None