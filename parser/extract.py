import ast
from typing import List
from state.function_state import get_functions_state

class ModuleImp:
    subnode_types = [ast.FunctionDef]

    @classmethod
    def get_functions_data(cls, node: ast.Module) -> List[ast.FunctionDef]:
        functions_data = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                functions_data.append(subnode)
        
        return functions_data

    @classmethod
    def extract(cls, node):
        pass


def extract(c_ast):
    functions = ModuleImp.get_functions(c_ast)
    f_state = get_functions_state(functions)

    # TODO extract the program