from typing import List

class CircuitState:
    def __init__(self) -> None:
        self.var_to_wire = {}
        # For now we think there is only one output
        self.out = {}
        self.gate_list = []
    
    # TODO write bytes from circuits
    def compile(self) -> bytes:
        pass

class Gate:
    def __init__(
        self,
        name: str,
        fan_in: List[int],
        fan_out: List[int]
    ) -> None:
        self.name = name
        self.fan_in = fan_in
        self.fan_out = fan_out
