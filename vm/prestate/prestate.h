#ifndef __PRESTATE_H__
#define __PRESTATE_H__

#include "../types.h"

#include <vector>
#include <functional>
#include <memory>

namespace prestate {

    struct Box;
    struct Node;
    struct Graph;

    typedef std::vector<std::shared_ptr<Box>> box_set;
    typedef std::pair<std::shared_ptr<Node>, int> Pin;

    struct Box {
        bool solid;
        bool sync; // need all inputs be filled
        bool controller; // flow control box
        FUNC_ID id;
        
        int inputs_sz, outputs_sz, locals_sz;
        std::unique_ptr<Graph> graph;

        /*
        * for solid boxes
        * for now just one out pin
        */
        std::function<PRIMITIVE_PTR(const std::vector<PRIMITIVE_PTR>&)> func;
        std::function<bool(const std::vector<PRIMITIVE_PTR>&)> check;
    };

    struct Node {
        std::shared_ptr<Box> box;
        std::vector<std::vector<Pin>> out;

        /*
        * index: index in graph
        * in_index: index in sources if it is an input pin for the graph
        * out_index: same as in_index but for output pins
        */
        int index, in_index, out_index;

        Node(std::shared_ptr<Box> box, int index=-1, int in_index=-1, int out_index=-1):
            box(box), index(index), in_index(in_index), out_index(out_index) {
                for(int i=0 ; i<box->outputs_sz ; i++)
                    out.push_back(std::vector<Pin>());
            }

    };

    struct Graph {
        std::vector<std::shared_ptr<Node>> nodes, sinks, sources;
        std::vector<std::pair<Pin, PRIMITIVE_PTR> > initials;

        Graph() {
        }

        Graph(const Graph &other) {
            operator=(other);
        }

        Graph& operator = (const Graph &other) {
            nodes = other.nodes;
            sinks = other.sinks;
            sources = other.sources;
            initials = other.initials;
            
            return *this;
        }

        void
        add_node(std::shared_ptr<Node> node, bool in=false, bool out=false) {
            node->index = nodes.size();
            nodes.push_back(node);
            
            if(in){
                node->in_index = sources.size();
                sources.push_back(node);
            }
            
            if(out){
                node->out_index = sinks.size();
                sinks.push_back(node);
            }
        }
    };

}

#endif