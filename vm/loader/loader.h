#ifndef ___LOADER_H__
#define ___LOADER_H__

#include "../prestate/prestate.h"
#include "../types.h"

#include <vector>
#include <string>
#include <memory>

const int BUFFER_SIZE = 1024;

std::vector<unsigned char>
read_code(const char *path);

std::pair<prestate::box_set, FUNC_ID>
load_code(const char *path);

#endif