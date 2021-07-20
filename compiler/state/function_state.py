import ast
from typing import List, Dict
from gen.function import get_new_id

class FunctionState:

    def __init__(self, id, fdef: ast.FunctionDef):
        self.id: int = id
        self.name: str = fdef.name
        self.fdef: ast.FunctionDef = fdef
        self.args: List[str] = [it.arg for it in fdef.args.args]
        self.out_num = 1 # TODO 1 for now

def get_functions_state(functions: List[ast.FunctionDef]) -> Dict[str, FunctionState]:
    ret = {}
    for function in functions:
        current_fstate = FunctionState(get_new_id(function.name), function)
        ret[current_fstate.name] = current_fstate
    
    return ret