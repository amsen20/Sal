#ifndef __PRESTATE_H__
#define __PRESTATE_H__

#include <vector>
#include <memory>

namespace prestate {
    struct Graph
    {};

    struct Box
    {};

    typedef std::vector<std::shared_ptr<Box>> box_set;
}

#endif