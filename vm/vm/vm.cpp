#define DEBUG
#define THREAD_NUM 2

#include "vm.h"
#include "../state/state.h"
#include "../concurrentqueue/blockingconcurrentqueue.h"
#include "../consts.h"

#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>

#ifdef DEBUG
#   include <iostream>
#endif

typedef moodycamel::BlockingConcurrentQueue<state::Flow> Queue;

std::atomic_int on; // TODO search for the memory order

void job(int id, Queue &q) {
#ifdef DEBUG
    std::cerr << "thread id: " << id << " started working.\n";
#endif
    
    moodycamel::ProducerToken ptok(q);

    state::Flow flow;
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
vm::run(prestate::box_set boxes) {
    Queue q;
    on.store(1);

#ifdef DEBUG
    std::cerr << "Running on: " << THREAD_NUM << " threads\n";
#endif

    std::vector<std::thread> threads;
    for(int i=0 ; i<THREAD_NUM ; i++)
        threads.push_back(std::thread(job, i, std::ref(q)));

    // TODO find and run main

    for(auto &&thread: threads)
        thread.join();

#ifdef DEBUG
    std::cerr << "finished." << "\n";
#endif
    
    return RUN_OK;
}