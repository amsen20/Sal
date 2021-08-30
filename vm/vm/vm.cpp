/*
* TODO: for now there is no support for raising exceptions if two flow come to a same pin.
*/

#define DEBUG
#define THREAD_NUM 2

#include "vm.h"
#include "../utils/utils.h"
#include "../state/state.h"
#include "../concurrentqueue/blockingconcurrentqueue.h"
#include "../consts.h"

#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>

// #ifdef DEBUG
#   include <iostream>
// #endif

using state::Flow;

typedef moodycamel::BlockingConcurrentQueue<Flow> Queue;

std::atomic_int on; // TODO search for the memory order

void
flow_initials(Queue &q, const std::shared_ptr<state::Node> &node);

std::shared_ptr<state::Node>
clone_lazy(
    Queue &q,
    std::shared_ptr<state::Node> par,
    std::shared_ptr<prestate::Node> pre_node
) {
    auto &&child = par->childs[pre_node->index];
    auto &&mtx = par->childs_mutex[pre_node->index];
    if(!std::atomic_load(&child)) {
        mtx.lock();
        if(std::atomic_load(&child))
            return child;
        child = std::make_shared<state::Node>(pre_node, par);
        flow_initials(q, child);
        mtx.unlock();
    }

    return child;
}

void
flow_out(
    Queue &q,
    PRIMITIVE_PTR value,
    const std::vector<prestate::Pin> &pins,
    const std::shared_ptr<state::Node> &node
) {
    for(auto &&pin: pins) {
        auto cln = clone_lazy(q, node, pin.first);
        q.enqueue(Flow(value, state::Pin(cln, pin.second)));
    }
}

void
flow_initials(Queue &q, const std::shared_ptr<state::Node> &node) {
    if(node->get_box()->solid)
        return;
    for(auto &&it: node->get_box()->graph->initials) {
        auto pin = it.first;
        auto value = it.second;
        auto cln = clone_lazy(q, node, pin.first);
        q.enqueue(Flow(value, state::Pin(cln, pin.second)));
    }
}

void
job(
    int id,
    Queue &q,
    const std::shared_ptr<state::Node> &main_node,
    std::vector<PRIMITIVE_PTR> &outs
) {
#ifdef DEBUG
    std::cerr << "thread id: " << id << " started working.\n";
#endif
    
    moodycamel::ProducerToken ptok(q);

    Flow flow;
    while(true) {
        q.wait_dequeue(flow);
        
        on ++;
        do {
            if(!flow.second.first)
                break;
            auto value = flow.first;
            auto node = flow.second.first;
            auto pin_index = flow.second.second;
            auto prenode = node->prenode;
            auto box = prenode->box;

            if(box->solid) {
                // TODO check pin should be none before.
                node->inputs[pin_index] = value; // TODO free the flow
                node->filled_inputs ++; // check memory order

                if(box->id == OUT_PIN_ID) {
                    auto index = prenode->out_index;
                    auto par_node = node->par;

                    if(main_node == par_node) {
                        outs[index] = value;
                        continue;
                    }

                    flow_out(
                        q,
                        value,
                        par_node->prenode->out[index],
                        par_node->par
                    );
                    continue;
                }

                if(!box->sync || node->filled_inputs == box->inputs_sz) {
                    if(box->controller && !box->check(node->inputs))
                        continue;

                    auto out = box->id == JOIN_ID ? value : box->func(node->inputs); // FIXME
                    flow_out(
                        q,
                        out,
                        prenode->out[0],
                        node->par
                    );

                    continue;
                }

                continue;
            }

            // not solid
            auto input_prenode = box->graph->sources[pin_index];
            flow_out(
                q,
                value,
                input_prenode->out[0],
                node
            );
        }while(q.try_dequeue(flow));
        
        on --;
        if (!on) {
            q.enqueue(state::Flow(nullptr, state::Pin(nullptr, -1)));

#ifdef DEBUG
            std::cerr << "thread id: " << id << " finished working.\n";
#endif
            return;
        }

#ifdef DEBUG
        std::cerr << "for thread id: " << id << " queue is empty but someone is working.\n";
#endif
    }
}

int
vm::run(const std::pair<prestate::box_set, FUNC_ID> &boxes_and_main_id) {
    auto boxes = boxes_and_main_id.first;
    auto main_id = boxes_and_main_id.second;
    Queue q;
    on.store(0); // TODO remove

#ifdef DEBUG
    std::cerr << "Running on: " << THREAD_NUM << " threads\n";
#endif

    std::shared_ptr<prestate::Box> main = nullptr;
    for(auto &&box: boxes)
        if(box->id == main_id) {
            main = box;
            break;
        }

    if(!main) {
        std::cout << "main function should exists.\n";
        exit(0);
    }

    std::shared_ptr<prestate::Node> main_prenode = std::make_shared<prestate::Node>(main);
    std::shared_ptr<state::Node> main_node = std::make_shared<state::Node>(main_prenode);
    
    flow_initials(q, main_node);
    std::vector<PRIMITIVE_PTR> outs(main->outputs_sz);
    for(int i=0 ; i<main->inputs_sz ; i++) {
        std::cout << "Enter: ";
        int64_t dat;
        std::cin >> dat;
        q.enqueue(Flow((PRIMITIVE_PTR)dat, state::Pin(main_node, i)));
    }

    std::vector<std::thread> threads;
    for(int i=0 ; i<THREAD_NUM ; i++)
        threads.push_back(std::thread(
            job,
            i,
            std::ref(q),
            std::ref(main_node),
            std::ref(outs)
        ));


    for(auto &&thread: threads)
        thread.join();

    for(int i=0 ; i<main->outputs_sz ; i++)
        std::cout << (int64_t)outs[i] << "\n";

#ifdef DEBUG
    std::cerr << "finished." << "\n";
#endif
    
    return RUN_OK;
}