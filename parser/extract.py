import ast
from copy import deepcopy
from state.circuit_state import END_GATE
from state.circuit_state import get_out_gate
from utils import get_wire_bytearray, get_function_bytearray
from gen.wire import get_new_id
from state.circuit_state import CircuitState
from utils import is_allowed
from decorators import register_impl, type_to_class
from typing import List
from state.function_state import get_functions_state
from extract import NotAllowedSubnode

@register_impl(type=ast.Module)
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
        circuit_state = CircuitState()
        circuit_state.functions_state = inherit_state.functions_state
        fstate = circuit_state.functions_state[node.name]
        circuit_state.code = get_function_bytearray(fstate.id)
        circuit_state.code += len(fstate.args).to_bytes(1, "big")
        for arg in fstate.args:
            wire_id = get_new_id()
            circuit_state.in_to_wire[arg] = wire_id
            circuit_state.code += get_wire_bytearray(wire_id)
        circuit_state.code += b'\x01' # number of outputs

        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state: CircuitState = impl.extract(subnode, circuit_state)
            circuit_state.code += subnode_circuit_state.code
            circuit_state.out_wires += subnode_circuit_state.out_wires
            circuit_state.gate_list += subnode_circuit_state.gate_list
        for wire_out in circuit_state.out_wires:
            circuit_state.add_gate(get_out_gate(wire_out))
        circuit_state.add_gate(END_GATE)

        return circuit_state

def extract(c_ast):
    functions = ModuleImp.get_functions(c_ast)
    f_state = get_functions_state(functions)
    ModuleImp.extract(c_ast, f_state)
    # TODO extract the program