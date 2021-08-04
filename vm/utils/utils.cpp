#include "utils.h"

int32_t
__4bytes_to_int(unsigned char *ptr) {
    int32_t ret = 0;
    for(int i=0 ; i<4 ; i++)
        ret = ret << 8 | ptr[i];
    
    return ret;
}