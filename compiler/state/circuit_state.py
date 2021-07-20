from local_types import VarName, WireId, Id, Environment
from consts import END_GATE_ID
from consts import OUT_GATE_ID
from utils import get_wire_bytearray
from utils import get_function_bytearray
from state.function_state import FunctionState
from typing import Dict, List

class Gate:
    def __init__(
        self,
        id: Id,
        name: VarName,
        fan_in: List[WireId],
        fan_out: List[WireId]
    ) -> None:
        self.id = id
        self.name: VarName = name
        self.fan_in: List[WireId] = fan_in
        self.fan_out: List[WireId] = fan_out
    
    def get_code(self) -> bytearray:
        code = get_function_bytearray(self.id)
        for wire_in in self.fan_in:
            code += get_wire_bytearray(wire_in)
        for wire_out in self.fan_out:
            code += get_wire_bytearray(wire_out)
        return code

class CircuitState:
    def __init__(self) -> None:
        self.var_to_wire: Dict[VarName, WireId] = {}
        # For now we think there is only one output
        self.functions_state: Dict[VarName, FunctionState] = {}
        self.in_to_wire: Environment = {}
        self.out_wires: List[WireId] = []
        self.gate_list: List[Gate] = []
        self.code: bytearray = bytearray()
    
    def add_gate(self, gate: Gate):
        self.gate_list.append(gate)
        self.code += gate.get_code()

END_GATE = Gate(END_GATE_ID, "end", [], [])

def get_out_gate(wire): 
    return Gate(OUT_GATE_ID, "out", wire, [])