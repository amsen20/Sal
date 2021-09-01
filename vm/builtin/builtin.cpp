#include "builtin.h"
#include "../consts.h"

#include <memory>

std::shared_ptr<Box> __add, __mul, __div, __not, __assign, __cond;
std::shared_ptr<Box> __join, __sub, __in_pin, __out_pin, __power_pin;
std::shared_ptr<Box> __pow, __lt, __lte;

std::map<FUNC_ID, std::shared_ptr<Box>>
set_up() {
    std::map<FUNC_ID, std::shared_ptr<Box>> id_to_box;

    auto reg = [&id_to_box](const std::shared_ptr<Box> &box) {
        id_to_box[box->id] = box;
    };

    __in_pin = std::make_shared<Box>(true, IN_PIN_ID, 0, 1);
    reg(__in_pin);

    __out_pin = std::make_shared<Box>(true, OUT_PIN_ID, 1, 0);
    reg(__out_pin);

    __power_pin = std::make_shared<Box>(true, POWER_PIN_ID, 1, 1);
    __power_pin->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return args[0]; // FIXME one output for function
    };
    reg(__power_pin);

    __assign = std::make_shared<Box>(true, ASSIGN_ID, 2, 1);
    __assign->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return args[1];
    };
    reg(__assign);

    __cond = std::make_shared<Box>(true, CONDITION_ID, 2, 1);
    __cond->controller = true;
    __cond->check = [](const std::vector<PRIMITIVE_PTR> &args) -> bool {
        return (bool)args[1];
    };
    __cond->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return args[0];
    };
    reg(__cond);

    __not = std::make_shared<Box>(true, NOT_ID, 1, 1);
    __not->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)(!(bool)args[0]);
    };
    reg(__not);

    __join = std::make_shared<Box>(true, JOIN_ID, 2, 1);
    __join->sync = false;
    reg(__join);

    __add = std::make_shared<Box>(true, ADD_ID, 2, 1);
    __add->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] + (int64_t)args[1]);
    };
    reg(__add);

    __mul = std::make_shared<Box>(true, MUL_ID, 2, 1);
    __mul->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] * (int64_t)args[1]);
    };
    reg(__mul);

    __div = std::make_shared<Box>(true, DIV_ID, 2, 1);
    __div->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] / (int64_t)args[1]);
    };
    reg(__div);

    __sub = std::make_shared<Box>(true, SUB_ID, 2, 1);
    __sub->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] - (int64_t)args[1]);
    };
    reg(__sub);

    __pow = std::make_shared<Box>(true, POW_ID, 2, 1);
    __pow->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)pow((int64_t)args[0], (int64_t)args[1]));
    };
    reg(__pow);

    __lt = std::make_shared<Box>(true, LT_ID, 2, 1);
    __lt->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] < (int64_t)args[1]);
    };
    reg(__lt);

    __lte = std::make_shared<Box>(true, LTE_ID, 2, 1);
    __lte->func = [](const std::vector<PRIMITIVE_PTR> &args) -> PRIMITIVE_PTR {
        return (PRIMITIVE_PTR)((int64_t)args[0] <= (int64_t)args[1]);
    };
    reg(__lte);

    return id_to_box;
}