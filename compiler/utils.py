def is_allowed(cls, obj):
    try:
        for allowed in cls.subnode_allowed_types:
            if isinstance(obj, allowed):
                return True
    except: # TODO
        pass
    return False

def get_wire_bytearray(id: int) -> bytearray:
    return id.to_bytes(4, "big")

def get_function_bytearray(id: int) -> bytearray:
    return id.to_bytes(4, "big")