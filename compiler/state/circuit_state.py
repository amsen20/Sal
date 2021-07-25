from local_types import VarName, WireId, Id, Environment, FunctionName
from consts import END_GATE_ID, BIN_OP_CODE, RESERVED_FUNCTION_IDS, SIZEOF, CONSTANT_GATE_ID
from consts import OUT_GATE_ID
from utils import get_wire_bytearray
from utils import get_function_bytearray
from state.function_state import FunctionState
from typing import Dict, List

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
    
    def add_gate(self, gate: Gate):
        self.gate_list.append(gate)
        self.code += gate.get_code()
    
    def add_gates(self, gates: List[Gate]):
        for gate in gates:
            self.add_gate(gate)

END_GATE = Gate(END_GATE_ID, "end", [], [])

def get_out_gate(wire): 
    return Gate(OUT_GATE_ID, "out", [wire], [])

def get_bin_op_gate(op, out_wire, in1_wire, in2_wire):
    func_id = BIN_OP_CODE[type(op)]
    return Gate(func_id, RESERVED_FUNCTION_IDS[func_id], [in1_wire, in2_wire], [out_wire])

def get_constant_gate(value, out_wire):
    return Gate(CONSTANT_GATE_ID, "const", [SIZEOF[type(value)], value], [out_wire])
