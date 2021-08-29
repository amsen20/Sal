#ifndef __STATE_H__
#define __STATE_H__

#include "../prestate/prestate.h"

#include <atomic>
#include <mutex>

namespace state {
    struct Node {
        std::shared_ptr<prestate::Node> prenode;
        std::shared_ptr<Node> par;
        std::vector<std::shared_ptr<Node>> childs; // treat them atomic
        std::vector<std::mutex> childs_mutex;

        /*
        * for solid boxes
        */
        std::vector<PRIMITIVE_PTR> inputs;
        std::atomic_int filled_inputs;

        std::shared_ptr<prestate::Box> get_box();
        
        Node(std::shared_ptr<prestate::Node> prenode=nullptr, std::shared_ptr<Node> par=nullptr):
            prenode(prenode), par(par) {
                if(prenode && get_box()->graph) {
                    childs.resize(get_box()->graph->nodes.size(), nullptr);
                    childs_mutex.resize(get_box()->graph->nodes.size());
                }
                filled_inputs = 0;
                if(get_box()->solid)
                    inputs.resize(get_box()->inputs_sz, nullptr);
            }
    };

    typedef std::pair<std::shared_ptr<Node>, int> Pin;
    typedef std::pair<PRIMITIVE_PTR, Pin> Flow;
}

#endif