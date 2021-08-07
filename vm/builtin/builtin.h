#ifndef __BUILTIN_H__
#define __BUILTIN_H__

#include "../prestate/prestate.h"
#include "../types.h"

#include <memory>
#include <map>

using prestate::Box;

std::shared_ptr<Box> __add, __mul, __and, __or, __not, __assign, __cond;
std::shared_ptr<Box> __cmp, __conn, __in_pin, __out_pin, __power_pin;

void
set_up(std::map<FUNC_ID, std::shared_ptr<Box>>&);

#endif