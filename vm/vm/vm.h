#ifndef __VM_H__
#define __VM_H__

#include "../types.h"
#include "../prestate/prestate.h"

namespace vm {
    int
    run(std::pair<prestate::box_set, FUNC_ID>);
}

#endif