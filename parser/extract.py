import ast
from copy import deepcopy
from gen.function import get_new_id
from state.circuit_state import CircuitState
from utils import is_allowed
from decorators import register_impl, type_to_class
from typing import List
from state.function_state import get_functions_state
from extract import NotAllowedSubnode

@register_impl(ast.Module)
class ModuleImp:
    subnode_allowed_types = {ast.FunctionDef}

    @classmethod
    def get_functions_data(cls, node: ast.Module) -> List[ast.FunctionDef]:
        functions_data = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                functions_data.append(subnode)
        
        return functions_data
    
    @classmethod
    def extract(
        cls,
        node: ast.Module,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = deepcopy(inherit_state)
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            circuit_state.code += impl.extract(subnode, circuit_state).code
        return circuit_state
            
@register_impl(type=ast.FunctionDef)
class FunctionDefImpl:
    subnode_allowed_types = {ast.Assign, ast.Return}

    @classmethod
    def extract(
        cls,
        node: ast.FunctionDef,
        inherit_state: CircuitState # TODO define state for each node type
    ) -> CircuitState:
        function_id = get_new_id()
        

def extract(c_ast):
    functions = ModuleImp.get_functions(c_ast)
    f_state = get_functions_state(functions)
    ModuleImp.extract(c_ast, f_state)
    # TODO extract the program