import ast
from typing import List, Dict
from gen.function import get_new_id

class FunctionState:

    def __init__(self, id, name, args, out_num):
        self.id: int = id
        self.name: str = name #What to do with fdef
        #self.fdef: ast.FunctionDef = fdef 
        self.args: List[str] = [it.arg for it in args.args]
        self.out_num = out_num # TODO 1 for now

def get_functions_state(functions: List[ast.FunctionDef]) -> Dict[str, FunctionState]:
    ret = {}
    for function in functions:
        current_fstate = FunctionState(get_new_id(function.name), function.name, function.args, 1)
        ret[current_fstate.name] = current_fstate
    return ret
    
