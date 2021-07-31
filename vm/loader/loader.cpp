#include "loader.h"

#include <fstream>

std::vector<unsigned char>
read_code(const char *path) {
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<unsigned char> code(size);
    file.read((char*)code.data(), size);

    return code;
}

/*
    <code> = NULL | <code><box desc>
    <box desc> = <box header><graph desc><end gate>
    <box header> = <box id><number of inputs><input wires><number of outputs>
*/
prestate::box_set
load_code(const char *path) {
    auto code = read_code(path);

    
}