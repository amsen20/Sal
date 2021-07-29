#include <iostream>
#include "concurrentqueue.h"

int main(int, char**) {
    moodycamel::ConcurrentQueue<int> q;
    q.enqueue(25);
    int item;
    bool found = q.try_dequeue(item);
    std::cout << found << ", " << item << "\n";
}
