import ast
from copy import deepcopy
from state.circuit_state import END_GATE, get_bin_op_gate, get_constant_gate
from state.circuit_state import get_out_gate, Gate
from utils import get_wire_bytearray, get_function_bytearray
from gen.wire import get_new_id
from state.circuit_state import CircuitState
from utils import is_allowed, merge_envs
from decorators import register_impl, type_to_class
from typing import List, Tuple
from state.function_state import get_functions_state
from exceptions import NotAllowedSubnode

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
            subnode_cs = impl.extract(subnode, circuit_state)
            
            circuit_state.gate_list += subnode_cs.gate_list
            circuit_state.code += subnode_cs.code

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
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        fstate = circuit_state.functions_state[node.name]
        circuit_state.code = get_function_bytearray(fstate.id)
        circuit_state.code += len(fstate.args).to_bytes(1, "big")
        for arg in fstate.args:
            wire_id = get_new_id()
            circuit_state.in_to_wire[arg] = wire_id
            circuit_state.var_to_wire[arg] = wire_id
            circuit_state.code += get_wire_bytearray(wire_id)
        circuit_state.code += b'\x01' # number of outputs

        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state: CircuitState = impl.extract(subnode, circuit_state)
            circuit_state.var_to_wire = merge_envs(
                circuit_state.var_to_wire,
                subnode_circuit_state.var_to_wire
            )
            circuit_state.add_gates(subnode_circuit_state.gate_list)
            circuit_state.out_wires += subnode_circuit_state.out_wires
        for wire_out in circuit_state.out_wires:
            circuit_state.add_gate(get_out_gate(wire_out))
        circuit_state.add_gate(END_GATE)

        return circuit_state

@register_impl(type=ast.Assign)
class AssignImp:
    subnode_allowed_types = {ast.BinOp, ast.Expr, ast.Constant, ast.Name}

    @classmethod
    def extract(
        cls,
        node: ast.Assign,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire) # Should not modify inherit state
        
        assert len(node.targets) == 1 # TODO support more than one inputs
        
        target = node.targets[0].id
        subnode = node.value
        if not is_allowed(cls, subnode):
            raise NotAllowedSubnode
        impl = type_to_class[type(subnode)]
        subnode_circuit_state, output_wire = impl.extract(subnode, circuit_state)
        
        circuit_state.var_to_wire[target] = output_wire
        circuit_state.add_gates(subnode_circuit_state.gate_list)

        return circuit_state

@register_impl(type=ast.BinOp)
class BinOpImpl:
    subnode_allowed_types = {ast.BinOp, ast.Constant, ast.Name}

    @classmethod
    def extract(
        cls,
        node: ast.BinOp,
        inherit_state: CircuitState
    ) -> Tuple[CircuitState, int]:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)
        
        left = node.left
        right = node.right
        subnodes = [left, right]
        subnodes_data: List[Tuple[CircuitState, int]] = []
        
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state, output_wire = impl.extract(subnode, circuit_state)
            subnodes_data.append((subnode_circuit_state, output_wire))
        
        for cs, _ in subnodes_data:
            circuit_state.add_gates(cs.gate_list)
        output_wire = get_new_id()
        circuit_state.add_gate(
            get_bin_op_gate(node.op, output_wire, subnodes_data[0][1], subnodes_data[1][1])
        )

        return circuit_state, output_wire

@register_impl(type=ast.Constant)
class ConstantImpl:
    subnode_allowed_types = {int}

    @classmethod
    def extract(
        cls,
        node: ast.Constant,
        inherit_state: CircuitState
    ) -> Tuple[CircuitState, int]:
        if not is_allowed(cls, node.value):
            raise NotAllowedSubnode

        circuit_state = CircuitState()

        output_wire = get_new_id()
        circuit_state.add_gate(
            get_constant_gate(node.value, output_wire)
        )

        return circuit_state, output_wire


@register_impl(type=ast.Return)
class ReturnImpl:
    subnode_allowed_types = {ast.Expr, ast.BinOp, ast.Name}

    @classmethod
    def extract(
        cls,
        node: ast.Return,
        inherit_state: CircuitState
    ) -> CircuitState:
        subnode = node.value
        if not is_allowed(cls, subnode):
            raise NotAllowedSubnode
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        impl = type_to_class[type(subnode)]
        subnode_cs, output_wire = impl.extract(subnode, circuit_state)

        circuit_state.add_gates(subnode_cs.gate_list)
        circuit_state.out_wires.append(output_wire)

        return circuit_state

@register_impl(type=ast.Name)
class NameImpl:
    subnode_allowed_types = {}

    @classmethod
    def extract(
        cls,
        node: ast.Name,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        return circuit_state, circuit_state.var_to_wire[node.id]

@register_impl(type=ast.Call)
class CallImpl:
    subnode_allowed_types = {ast.Call, ast.Constant, ast.BinOp, ast.Name}

    @classmethod
    def extract(
        cls,
        node: ast.Call,
        inherit_state: CircuitState
    ) -> Tuple[CircuitState, int]:
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        output_args = []
        for arg in node.args:
            if not is_allowed(cls, arg):
                raise NotAllowedSubnode
            impl = type_to_class[type(arg)]
            arg_circuit_state, arg_output_wire = impl.extract(arg, circuit_state)
            circuit_state.add_gates(arg_circuit_state.gates_list)
            output_args.append(arg_output_wire)
        output_wire = get_new_id()
        func_id = circuit_state.functions_state[node.func.id].id
        circuit_state.add_gate(
            Gate(
                func_id,
                node.func.id,
                output_args,
                [output_wire]
            )
        )
        return circuit_state, output_wire

def extract(c_ast):
    functions = ModuleImp.get_functions_data(c_ast)
    circuit_state = CircuitState()
    circuit_state.functions_state = get_functions_state(functions)
    return ModuleImp.extract(c_ast,  circuit_state).code