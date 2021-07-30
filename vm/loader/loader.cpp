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