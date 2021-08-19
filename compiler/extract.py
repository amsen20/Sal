import ast
from compiler.state.function_state import FunctionState
from copy import deepcopy
from state.circuit_state import get_assign_gate, get_bin_op_gate, get_constant_gate
from state.circuit_state import get_not_gate, get_cond_gate, get_compare_gate, get_join_gate
from state.circuit_state import get_out_gate, Gate
from utils import get_description_length, get_wire_bytearray, get_function_bytearray
from gen.wire import get_new_id
from state.circuit_state import CircuitState
from utils import is_allowed, merge_envs
from decorators import register_impl, type_to_class
from typing import List, Tuple, Set
from state.function_state import get_functions_state
from exceptions import NotAllowedSubnode

@register_impl(type=ast.Module)
class ModuleImpl:
    subnode_allowed_types = {ast.FunctionDef}

    @classmethod
    def get_functions_data(cls, node: ast.Module) -> List[ast.FunctionDef]:
        functions_data = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                functions_data.append(subnode)
        
        return functions_data

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        return deepcopy(inherit_state)

    @classmethod
    def extract(
        cls,
        node: ast.Module,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)

        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_cs = impl.extract(subnode, circuit_state)
            
            circuit_state.gate_list += subnode_cs.gate_list
            circuit_state.code += subnode_cs.code

        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Module
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    def get_used_vars(
        cls,
        node: ast.Module
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars

    @classmethod
    def get_hidden_functions_data(cls, node: ast.Module) -> List[FunctionState]:
        functions_data = []
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data
       
@register_impl(type=ast.FunctionDef)
class FunctionDefImpl:
    subnode_allowed_types = {ast.Assign, ast.Return, ast.If}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.FunctionDef,
        inherit_state: CircuitState # TODO define state for each node type
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)

        fstate = circuit_state.functions_state[node.name]
        circuit_state.code = get_function_bytearray(fstate.id)
        length_index = len(circuit_state.code)
        circuit_state.code += len(fstate.args).to_bytes(1, "big")
        
        for arg in fstate.args:
            wire_id = get_new_id()
            circuit_state.in_to_wire[arg] = wire_id
            circuit_state.var_to_wire[arg] = wire_id
            circuit_state.code += get_wire_bytearray(wire_id)
        
        circuit_state.code += b'\x01' # number of outputs

        used_vars = cls.get_defined_vars(node)
        local_vars = list(filter(lambda x: x not in fstate.args, used_vars))
        circuit_state.code += len(local_vars).to_bytes(1, "big") # number of local vars
        for local_var in local_vars:
            wire_id = get_new_id()
            circuit_state.var_to_wire[local_var] = wire_id
            circuit_state.code += get_wire_bytearray(wire_id)

        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state: CircuitState = impl.extract(subnode, circuit_state) # TODO check if finished
            circuit_state.var_to_wire = merge_envs(
                circuit_state.var_to_wire,
                subnode_circuit_state.var_to_wire
            )
            circuit_state.add_gates(subnode_circuit_state.gate_list)
            circuit_state.out_wires += subnode_circuit_state.out_wires
        for wire_out in circuit_state.out_wires:
            circuit_state.add_gate(get_out_gate(wire_out))
        
        circuit_state.code = circuit_state.code[:length_index] + \
            get_description_length(len(circuit_state.code)) + \
                circuit_state.code[length_index:]

        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.FunctionDef
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.FunctionDef
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for arg in node.args: #TODO support arg types
            vars.add(arg.arg)
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars

    @classmethod
    def get_hidden_functions_data(cls, node: ast.FunctionDef) -> List[FunctionState]:
        functions_data = []
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data

    

@register_impl(type=ast.Assign)
class AssignImpl:
    subnode_allowed_types = {ast.BinOp, ast.Constant, ast.Name, ast.Call}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire) # Should not modify inherit state

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.Assign,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)
        
        assert len(node.targets) == 1 # TODO support multiple assignment
        
        target = node.targets[0].id
        subnode = node.value
        if not is_allowed(cls, subnode):
            raise NotAllowedSubnode
        impl = type_to_class[type(subnode)]
        subnode_circuit_state = impl.extract(subnode, circuit_state)
        
        circuit_state.add_gates(subnode_circuit_state.gate_list)
        
        assign_to_wire = subnode_circuit_state.output_wire
        var_new_wire = get_new_id()
        circuit_state.add_gate(
            get_assign_gate(
                lvalue_wire=circuit_state.var_to_wire[target],
                rvalue_wire=assign_to_wire,
                target_wire=var_new_wire
            )
        )
        circuit_state.var_to_wire[target] = var_new_wire

        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Assign
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.targets:
            vars.add(subnode.id)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.Assign
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.targets:
            vars.add(subnode)
        impl = type_to_class[type(node.value)]
        value_vars = impl.get_used_vars(node.value)
        vars = vars.union(value_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Assign) -> List[FunctionState]:
        functions_data = []
        subnode = node.value #TODO multiple assign
        impl = type_to_class[type(subnode)]
        functions_data += impl.get_hiddin_functions_data(subnode)
        return functions_data

        
    

@register_impl(type=ast.BinOp)
class BinOpImpl:
    subnode_allowed_types = {ast.BinOp, ast.Constant, ast.Name, ast.Call}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.BinOp,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)
        
        left = node.left
        right = node.right
        subnodes = [left, right]
        subnodes_data: List[CircuitState] = []
        
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state = impl.extract(subnode, circuit_state)
            output_wire  = subnode_circuit_state.output_wire
            subnodes_data.append(subnode_circuit_state)
        
        for cs in subnodes_data:
            circuit_state.add_gates(cs.gate_list)
        output_wire = get_new_id()
        circuit_state.add_gate(
            get_bin_op_gate(node.op, output_wire, subnodes_data[0].output_wire, subnodes_data[1].output_wire)
        )
        circuit_state.output_wire = output_wire

        return circuit_state
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.BinOp
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        left = node.left
        right = node.right
        subnodes = [left, right]
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.BinOp
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        left = node.left
        right = node.right
        subnodes = [left, right]
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.BinOp) -> List[FunctionState]:
        functions_data = []
        subnodes = [node.left, node.right]
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data
    

@register_impl(type=ast.Constant)
class ConstantImpl:
    subnode_allowed_types = {int}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        return CircuitState()

    @classmethod
    def extract(
        cls,
        node: ast.Constant,
        inherit_state: CircuitState
    ) -> CircuitState:
        if not is_allowed(cls, node.value):
            raise NotAllowedSubnode

        circuit_state = cls.clone_inherit_state(inherit_state)

        output_wire = get_new_id()
        circuit_state.add_gate(
            get_constant_gate(node.value, output_wire)
        )
        circuit_state.output_wire = output_wire

        return circuit_state
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Constant
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        return vars
    def get_used_vars(
        cls,
        node: ast.Constant
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Constant) -> List[FunctionState]:
        functions_data = []
        return functions_data


@register_impl(type=ast.Return)
class ReturnImpl:
    subnode_allowed_types = {ast.BinOp, ast.Name, ast.Call}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.Return,
        inherit_state: CircuitState
    ) -> CircuitState:
        subnode = node.value
        if not is_allowed(cls, subnode):
            raise NotAllowedSubnode
        circuit_state = cls.clone_inherit_state(inherit_state)

        impl = type_to_class[type(subnode)]
        subnode_cs = impl.extract(subnode, circuit_state)

        circuit_state.add_gates(subnode_cs.gate_list)
        circuit_state.out_wires.append(subnode_cs.output_wire)

        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Return
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in [node.value]:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars

    @classmethod
    def get_used_vars(
        cls,
        node: ast.Return
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in [node.value]:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Return) -> List[FunctionState]:
        functions_data = []
        for subnode in [node.value]:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data

@register_impl(type=ast.Name)
class NameImpl:
    subnode_allowed_types = {}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.Name,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)

        circuit_state.output_wire = circuit_state.var_to_wire[node.id]
        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Name
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        return vars

    @classmethod
    def get_used_vars(
        cls,
        node: ast.Name
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        vars.add(node.id)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Name) -> List[FunctionState]:
        functions_data = []
        return functions_data

@register_impl(type=ast.Call)
class CallImpl:
    subnode_allowed_types = {ast.Call, ast.Constant, ast.BinOp, ast.Name}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.Call,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)

        output_args = []
        for arg in node.args:
            if not is_allowed(cls, arg):
                raise NotAllowedSubnode
            impl = type_to_class[type(arg)]
            arg_circuit_state = impl.extract(arg, circuit_state)
            arg_output_wire = arg_circuit_state.output_wire
            circuit_state.add_gates(arg_circuit_state.gate_list)
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
        circuit_state.output_wire = output_wire

        return circuit_state
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Call
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.args:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.Call
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.args:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Call) -> List[FunctionState]:
        functions_data = []
        for subnode in node.args:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data

@register_impl(type=ast.If)
class IfImpl:
    subnode_allowed_types = {ast.Assign, ast.If, ast.Return, ast.While, ast.Call}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.If,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)
        used_vars = cls.get_defined_vars(node)
        
        prev_var_to_wire = deepcopy(circuit_state.var_to_wire)
        cond_impl = type_to_class[type(node.test)] # TODO check it is testable or not
        cond_circuit: CircuitState = cond_impl.extract(node.test, circuit_state)
        cond_wire = cond_circuit.output_wire
        circuit_state.add_gates(cond_circuit.gate_list)
        
        for used_var in used_vars:
            old_wire = circuit_state.var_to_wire[used_var]
            new_wire = get_new_id()
            circuit_state.add_gate(get_cond_gate(old_wire, cond_wire, new_wire))
            circuit_state.var_to_wire[used_var] = new_wire

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
        
        for used_var in used_vars:
            prev_var_wire = prev_var_to_wire[used_var]
            curr_var_wire = circuit_state.var_to_wire[used_var]
            not_cond_wire = get_new_id()
            circuit_state.add_gate(get_not_gate(cond_wire, not_cond_wire))
            main_var_wire = get_new_id()
            circuit_state.add_gate(get_cond_gate(prev_var_wire, not_cond_wire, main_var_wire))
            new_wire = get_new_id()
            circuit_state.add_gate(get_join_gate(main_var_wire, curr_var_wire, new_wire))
        
        return circuit_state

    @classmethod
    def get_defined_vars(
        cls,
        node: ast.If
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.If
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        impl = type_to_class[type(node.test)]
        test_vars = impl.get_used_vars(node.test)
        vars = vars.union(test_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.If) -> List[FunctionState]:
        functions_data = []
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        impl = type_to_class[type(node.test)]
        test_functions_data = impl.get_hidden_functions_data(node.test)
        functions_data += test_functions_data
        return functions_data

@register_impl(type=ast.Compare)
class CompareImpl:

    subnode_allowed_types = {ast.BinOp, ast.Expr, ast.Constant, ast.Name}

    @classmethod
    def clone_inherit_state(
        cls,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = CircuitState()
        circuit_state.functions_state = deepcopy(inherit_state.functions_state)
        circuit_state.var_to_wire = deepcopy(inherit_state.var_to_wire)

        return circuit_state

    @classmethod
    def extract(
        cls,
        node: ast.Compare,
        inherit_state: CircuitState
    ) -> CircuitState:
        circuit_state = cls.clone_inherit_state(inherit_state)
        # TODO multiple comparators
        subnodes = [node.left, node.comparators[0]]
        subnodes_data: List[CircuitState] = []
        
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_circuit_state = impl.extract(subnode, circuit_state)
            subnodes_data.append(subnode_circuit_state)
        
        for cs in subnodes_data:
            circuit_state.add_gates(cs.gate_list)
        
        output_wire = get_new_id()
        # TODO multiple comparators
        circuit_state.add_gate(
            get_compare_gate(node.ops[0], output_wire, subnodes_data[0].output_wire, subnodes_data[1].output_wire)
        )
        circuit_state.output_wire = output_wire
        return circuit_state
    
    @classmethod
    def get_defined_vars(
        cls,
        node: ast.Compare
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.Compare
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        subnodes = [node.left, node.comparators[0]]
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            vars = vars.union(impl.get_used_vars(subnode))
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.Compare) -> List[FunctionState]:
        functions_data = []
        subnodes = [node.left, node.comparators[0]]
        for subnode in subnodes:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        return functions_data

@register_impl(type=ast.While)
class WhileImpl:
    
    subnode_allowed_types = {ast.Assign, ast.If, ast.Return, ast.While, ast.Call}

    @classmethod
    def get_defined_vars(
        cls,
        node: ast.While
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_defined_vars(subnode)
            vars = vars.union(subnode_vars)
        return vars
    
    @classmethod
    def get_used_vars(
        cls,
        node: ast.While
    ) -> Set[ast.Name]:
        vars: Set[ast.Name] = set()
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_vars = impl.get_used_vars(subnode)
            vars = vars.union(subnode_vars)
        impl = type_to_class[type(node.test)]
        test_vars = impl.get_used_vars(node.test)
        vars = vars.union(test_vars)
        return vars
    
    @classmethod
    def get_hidden_functions_data(cls, node: ast.While) -> List[FunctionState]:
        functions_data = []
        self_impl = type_to_class[type(node)]
        self_name = str(node.lineno)
        self_id = get_new_id(self_name)
        self_args = self_impl.get_used_vars(node)
        self_outs = self_impl.get_defined_vars(node)
        self_data = FunctionState(self_id, self_name, self_args, len(self_outs))
        functions_data.append(self_data)
        for subnode in node.body:
            if not is_allowed(cls, subnode):
                raise NotAllowedSubnode
            impl = type_to_class[type(subnode)]
            subnode_functions_data = impl.get_hidden_functions_data(subnode)
            functions_data += subnode_functions_data
        test_impl = type_to_class[type(node.test)]
        test_functions_data = test_impl.get_hidden_functions_data(node.test)
        functions_data += test_functions_data
        return functions_data



def extract(c_ast):
    functions = ModuleImpl.get_functions_data(c_ast)
    circuit_state = CircuitState()
    circuit_state.functions_state = get_functions_state(functions)
    final_cs = ModuleImpl.extract(c_ast,  circuit_state)
    print([str(gate) for gate in final_cs.gate_list])
    return final_cs.code