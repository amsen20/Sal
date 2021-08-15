#include "builtin.h"
#include "../consts.h"

#include <memory>

void
set_up(std::map<FUNC_ID, std::shared_ptr<Box>> &id_to_box) {
    __power_pin = std::make_shared<Box>();
    __power_pin->solid = true;
    __power_pin->sync = true;
    __power_pin->id = POWER_PIN_ID;
    __power_pin->inputs_sz = 1;
    __power_pin->outputs_sz = 1;
    __power_pin->func = [](void* args) -> void* {
        return args;
    };
}