import sys
import ast
from extract import extract

path = sys.argv[1]
with open(path, "r") as f:
    c_ast = ast.parse(f.read())

circuit = extract(c_ast)
with open("a.sal", "wb") as f:
    f.write(circuit)