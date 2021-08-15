from consts import COMPARE_CODE, COND_GATE_ID, JOIN_GATE_ID, NOT_GATE_ID
from local_types import VarName, WireId, Id, Environment, FunctionName
from consts import ASSIGN_GATE_ID, BIN_OP_CODE, RESERVED_FUNCTION_IDS, TYPE_CODE, CONSTANT_GATE_ID
from consts import OUT_GATE_ID
from utils import get_wire_bytearray
from utils import get_function_bytearray
from state.function_state import FunctionState
from typing import Dict, List
import ast

class Gate:
    def __init__(
        self,
        id: Id,
        name: FunctionName,
        fan_in: List[WireId],
        fan_out: List[WireId]
    ) -> None:
        self.id = id
        self.name: FunctionName = name
        self.fan_in: List[WireId] = fan_in
        self.fan_out: List[WireId] = fan_out
    
    def get_code(self) -> bytearray:
        code = get_function_bytearray(self.id)
        for wire_in in self.fan_in:
            code += get_wire_bytearray(wire_in) # Add features for constant values
        for wire_out in self.fan_out:
            code += get_wire_bytearray(wire_out)
        return code
    
    def __str__(self) -> str:
        return f"id: {self.id}, name: {self.name}, inputs: {self.fan_in}, outputs: {self.fan_out}"

class CircuitState:
    def __init__(self) -> None:
        self.var_to_wire: Environment = {}
        # For now we think there is only one output
        self.functions_state: Dict[FunctionName, FunctionState] = {}
        self.in_to_wire: Environment = {}
        self.out_wires: List[WireId] = []
        self.gate_list: List[Gate] = []
        self.code: bytearray = bytearray()

        # For states which have output
        self.output_wire: WireId = None
    
    def add_gate(self, gate: Gate):
        self.gate_list.append(gate)
        self.code += gate.get_code()
    
    def add_gates(self, gates: List[Gate]):
        for gate in gates:
            self.add_gate(gate)

# END_GATE = Gate(END_GATE_ID, "end", [], [])

def get_out_gate(wire): 
    return Gate(OUT_GATE_ID, "out", [wire], [])

def get_bin_op_gate(op, out_wire, in1_wire, in2_wire):
    func_id = BIN_OP_CODE[type(op)]
    return Gate(func_id, RESERVED_FUNCTION_IDS[func_id], [in1_wire, in2_wire], [out_wire])

def get_constant_gate(value, out_wire):
    return Gate(CONSTANT_GATE_ID, "const", [TYPE_CODE[type(value)], value], [out_wire])

def get_assign_gate(lvalue_wire, rvalue_wire, target_wire):
    return Gate(ASSIGN_GATE_ID, "assign", [lvalue_wire, rvalue_wire], [target_wire])

def get_cond_gate(in_wire, cond_wire, out_wire):
    return Gate(COND_GATE_ID, "cond", [in_wire, cond_wire], [out_wire]) 

def get_not_gate(in_wire, out_wire):
    return Gate(NOT_GATE_ID, "not", [in_wire], [out_wire])

def get_join_gate(in1_wire, in2_wire, out_wire):
    return Gate(JOIN_GATE_ID, "join", [in1_wire, in2_wire], [out_wire])

def get_compare_gate(op, out_wire, in1_wire, in2_wire):
    func_id = COMPARE_CODE[type(op)]
    if(func_id == COMPARE_CODE[ast.Gt]):
        func_id = COMPARE_CODE[ast.Lt]
        tmp_wire = in1_wire
        in1_wire = in2_wire
        in2_wire = tmp_wire
    if(func_id == COMPARE_CODE[ast.GtE]):
        func_id = COMPARE_CODE[ast.LtE]
        tmp_wire = in1_wire
        in1_wire = in2_wire
        in2_wire = tmp_wire
    func_name = RESERVED_FUNCTION_IDS[func_id]
    return Gate(func_id, func_name, [in1_wire, in2_wire], [out_wire])
