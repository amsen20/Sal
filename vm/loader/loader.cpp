#include "loader.h"
#include "../utils/utils.h"
#include "../prestate/prestate.h"

#include <fstream>
#include <map>

using prestate::Box;
using prestate::Graph;

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
    <box header> = <box id><number of inputs><input wires><number of outputs><number of local vars><local var wires>
*/
prestate::box_set
load_code(const char *path) {
    auto code = read_code(path);
    std::map<FUNC_ID, std::shared_ptr<Box>> id_to_box;
    std::vector<std::shared_ptr<Box>> boxes;

    // finding box definitions
    for(int it=0 ; it<code.size() ; ) { 
        int next = it;
        auto box = std::make_shared<Box>();
        boxes.push_back(box);
        
        FUNC_ID box_id = __4bytes_to_int(&code[it]);
        box->id = box_id;
        id_to_box[box_id] = box;
        it += sizeof(FUNC_ID);

        next += __4bytes_to_int(&code[it]);
        it += sizeof(FUNC_LENGTH);

        box->inputs_sz = code[it];
        it += 1 + code[it] * sizeof(WIRE_ID);

        box->outputs_sz = code[it];
        it += 1 + code[it] * sizeof(WIRE_ID);

        box->locals_sz = code[it];
        it += 1 + code[it] * sizeof(WIRE_ID);

        it = next;
    }

    for(int it=0 ; it<code.size() ; ) {
        int next = it;
        FUNC_ID box_id = __4bytes_to_int(&code[it]);
        std::shared_ptr<Box> box = id_to_box[box_id];
        std::unique_ptr<Graph> graph(new Graph());
        it += sizeof(FUNC_ID);

        next += __4bytes_to_int(&code[it]);
        it += sizeof(FUNC_LENGTH);

        it ++;
        // for(int i=0 ; i<box->inputs_sz ; i++) {
        //     graph->sources.push_back()
        // }

        box->graph = std::move(graph);
    }
}