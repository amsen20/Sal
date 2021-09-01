#include "loader.h"
#include "vm.h"
#include "../flags.h"

#include <iostream>

int main(int argc, char* argv[]) {
#ifdef MEASURE
    auto start = clock();
#endif

    if(argc < 2) {
        std::cout << "usage: salvm path/to/salfile\n";
        return 1;
    }
    vm::run(load_code(argv[1]));

#ifdef MEASURE
    std::cerr << "\nOverall time: " << 1000000 * (clock()-start) / CLOCKS_PER_SEC << "ns\n";
#endif
}
