#ifndef __UTILS_H__
#define __UTILS_H__

#include <stdint.h>
#include <string>

int32_t
__4bytes_to_int(unsigned char *ptr);

void 
finish(std::string msg);

template<typename ...Args>
void
ensuref(bool cond, Args&&... msg);

#endif