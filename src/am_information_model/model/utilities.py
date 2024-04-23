
__all__ = [
    "_serialize_to_data",
    "_deserialize_from_data"
]

def _serialize_to_data(obj):
    if obj is not None:
        if hasattr(obj, "data"):
            return obj.data
        else:
            raise AttributeError
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