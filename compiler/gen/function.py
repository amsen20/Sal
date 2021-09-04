import random
from consts import MAX_FUNCTION_ID, RESERVED_FUNCTION_IDS

function_ids = RESERVED_FUNCTION_IDS
current_id = 100 # FIXME

def get_new_id(name: str) -> int:
    global current_id

    while True:
        new_id = current_id # do it smarter
        if new_id in function_ids:
            current_id += 1
            continue
        function_ids[new_id] = name
        return new_id
