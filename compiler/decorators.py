from typing import Dict

type_to_class = {}

def register_impl(type):
    def func(cls):
        type_to_class[type] = cls
        return cls
    return func