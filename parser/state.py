import ast
from typing import List

class FunctionState:

    def __init__(self, id, fdef: ast.FunctionDef):
        self.id = id
        self.name = fdef.name
        self.fdef = fdef

def get_functions_state(functions: List[ast.FunctionDef]) -> List[FunctionState]:
    ret = {}
    id = 100 # do it smarter
    for function in functions:
        current_fstate = FunctionState(id, function)
        id += 1
        ret[current_fstate.name] = current_fstate
    
    return ret