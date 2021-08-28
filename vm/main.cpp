#include "loader.h"
#include "vm.h"

#include <iostream>

int main(int argc, char* argv[]) {
    if(argc < 2) {
        std::cout << "usage: salvm path/to/salfile\n";
        return 1;
    }
    vm::run(load_code(argv[1]));
}
