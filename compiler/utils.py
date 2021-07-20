from typing import Dict

from local_types import FunctionId, WireId, Environment, Id

def is_allowed(cls, obj):
    try:
        for allowed in cls.subnode_allowed_types:
            if isinstance(obj, allowed):
                return True
    except: # TODO
        pass
    return False

def get_wire_bytearray(id: WireId) -> bytearray:
    return id.to_bytes(4, "big")

def get_function_bytearray(id: FunctionId) -> bytearray:
    return id.to_bytes(4, "big")

def merge_envs(
    first_env: Environment,
    second_env: Environment
) -> Environment:
    ret_env: Environment = {}
    for k, v in first_env.items():
        ret_env[k] = v
    for k, v in second_env.items():
        ret_env[k] = v
    
    return ret_env