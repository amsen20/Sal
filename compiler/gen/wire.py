import random
from consts import MAX_WIRE_ID, RESERVED_WIRE_IDS

wire_ids = set()

def get_new_id():
    while True:
        new_id = random.randint(0, MAX_WIRE_ID) # do it smarter
        if new_id in RESERVED_WIRE_IDS and new_id in wire_ids:
            continue
        return new_id
