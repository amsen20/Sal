import ast

MAX_WIRE_ID = (1 << 32)
RESERVED_WIRE_IDS = set()

MAX_FUNCTION_ID = (1 << 32)

# END_GATE_ID = 0
OUT_GATE_ID = 1
CONSTANT_GATE_ID = 2
ASSIGN_GATE_ID = 3
COND_GATE_ID = 4
NOT_GATE_ID = 5

RESERVED_FUNCTION_IDS = {
    # 0: 'end',
    1: 'out',
    2: 'const',
    3: 'assign',
    4: 'cond',
    5: 'not',
    10: 'add',
    11: 'mult',
    12: 'div',
    13: 'sub',
    14: 'pow'
}

BIN_OP_CODE = {
    ast.Add: 10,
    ast.Mult: 11,
    ast.Div: 12,
    ast.Sub: 13,
    ast.Pow: 14
}

SIZEOF = {
    int: 4
}