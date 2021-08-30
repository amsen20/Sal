#ifndef __BUILTIN_H__
#define __BUILTIN_H__

#include "../prestate/prestate.h"
#include "../types.h"

#include <memory>
#include <map>

using prestate::Box;

// TODO check if static is ok.
static std::shared_ptr<Box> __add, __mul, __div, __not, __assign, __cond;
static std::shared_ptr<Box> __join, __sub, __in_pin, __out_pin, __power_pin;
static std::shared_ptr<Box> __pow, __lt, __lte;

std::map<FUNC_ID, std::shared_ptr<Box>>
set_up();

#endif