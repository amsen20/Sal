import random
from consts import MAX_FUNCTION_ID, RESERVED_FUNCTION_IDS

wire_ids = set()

def get_new_id():
    while True:
        new_id = random.randint(0, MAX_FUNCTION_ID) # do it smarter
        if new_id in RESERVED_FUNCTION_IDS and new_id in wire_ids:
            continue
        return new_id
