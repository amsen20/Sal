import random
from consts import MAX_WIRE_ID, RESERVED_WIRE_IDS

wire_ids = set()
current_id = 100 # FIXME

def get_new_id() -> int:
    global current_id

    while True:
        new_id = current_id # TODO do it smarter
        if new_id in RESERVED_WIRE_IDS or new_id in wire_ids:
            current_id += 1
            continue
        wire_ids.add(new_id)
        return new_id
