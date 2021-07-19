def is_allowed(cls, obj):
    try:
        for allowed in cls.subnode_allowed_types:
            if isinstance(obj, allowed):
                return True
    except: # TODO
        pass
    return False