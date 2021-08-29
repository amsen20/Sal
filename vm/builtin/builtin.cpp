#include "builtin.h"
#include "../consts.h"

#include <memory>

std::map<FUNC_ID, std::shared_ptr<Box>>
set_up() {
    std::map<FUNC_ID, std::shared_ptr<Box>> id_to_box;

    __in_pin = std::make_shared<Box>(true, IN_PIN_ID, 0, 1);
    id_to_box[__in_pin->id] = __in_pin;

    __out_pin = std::make_shared<Box>(true, OUT_PIN_ID, 1, 0);
    id_to_box[__out_pin->id] = __out_pin;

    __power_pin = std::make_shared<Box>(true, POWER_PIN_ID, 1, 1);
    __power_pin->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return args[0]; // FIXME one output for function
    };
    id_to_box[__power_pin->id] = __power_pin;

    __assign = std::make_shared<Box>(true, ASSIGN_ID, 2, 1);
    __assign->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return args[1];
    };

    return id_to_box;
}