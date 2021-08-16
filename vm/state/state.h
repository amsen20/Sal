#ifndef __STATE_H__
#define __STATE_H__

#include "../prestate/prestate.h"

#include <atomic>

namespace state {
    struct Node {
        std::shared_ptr<prestate::Node> prenode;
        std::shared_ptr<Node> par;
        std::vector<std::atomic<std::shared_ptr<Node>>> childs;

        /*
        * for solid boxes
        */
        std::vector<PRIMITIVE_PTR> inputs;
        int filled_inputs;

        std::shared_ptr<prestate::Box> get_box();
        
        Node(std::shared_ptr<prestate::Node> prenode=nullptr, std::shared_ptr<Node> par=nullptr):
            prenode(prenode), par(par) {
                if(prenode) {
                    if(get_box()->graph) {
                        childs.resize(get_box()->graph->nodes.size());
                        for(auto &&child: childs)
                            child.store(nullptr);
                    }
                }
            }
    };

    typedef std::pair<std::shared_ptr<Node>, int> Pin;
    typedef std::pair<PRIMITIVE_PTR, Pin> Flow;
}

#endif