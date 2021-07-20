import random
from consts import MAX_FUNCTION_ID, RESERVED_FUNCTION_IDS

function_ids = RESERVED_FUNCTION_IDS

def get_new_id(name: str) -> int:
    while True:
        new_id = random.randint(0, MAX_FUNCTION_ID) # do it smarter
        if new_id in function_ids:
            continue
        function_ids[name] = new_id
        return new_id
