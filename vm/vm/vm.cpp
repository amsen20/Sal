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
job(
    int id,
    Queue &q,
    const std::shared_ptr<state::Node> &main_node,
    std::vector<PRIMITIVE_PTR> &out
    )
{
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
            // TODO do the job
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
vm::run(std::pair<prestate::box_set, FUNC_ID> boxes_and_main_id) {
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
    ensuref(main != nullptr, "main function should exists.");

    std::shared_ptr<prestate::Node> main_prenode = std::make_shared<prestate::Node>(main);
    std::shared_ptr<state::Node> main_node = std::make_shared<state::Node>(main_prenode);
    
    flow_initials(main_node);
    std::vector<PRIMITIVE_PTR> outs(main->outputs_sz);
    for(int i=0 ; i<main->inputs_sz ; i++) {
        std::cout << "Enter: ";
        int32_t dat;
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
        std::cout << (int32_t)outs[i] << "\n";

#ifdef DEBUG
    std::cerr << "finished." << "\n";
#endif
    
    return RUN_OK;
}