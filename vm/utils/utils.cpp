#include "utils.h"

#include <iostream>

int32_t
__4bytes_to_int(unsigned char *ptr) {
    int32_t ret = 0;
    for(int i=0 ; i<4 ; i++)
        ret = ret << 8 | ptr[i];
    
    return ret;
}

void
finish(std::string msg){
    std::cerr << msg << "\n";
    exit(0);
}

template<typename ...Args>
void
ensuref(bool cond, Args&&... msg){
    if(cond)
        return;
    finish(get_str(msg...));
}