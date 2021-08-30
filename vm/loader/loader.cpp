#include "loader.h"
#include "../consts.h"
#include "../builtin/builtin.h"
#include "../utils/utils.h"
#include "../prestate/prestate.h"

#include <fstream>
#include <map>

using namespace prestate;

std::pair<PRIMITIVE_PTR, int>
read_const_value(TYPE_ID type_id, unsigned char *ptr){
    if(type_id == INTEGER_TYPE_ID)
        return {(PRIMITIVE_PTR)__4bytes_to_int(ptr), 4};
    // TODO add list
}

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
    <code> = <main func id><code body>
    <code body> = NULL | <code body><box desc>
    <box desc> = <box header><graph desc><end gate>
    <box header> = <box id><number of inputs><input wires><number of outputs><number of local vars><local var wires>
    <graph desc> = NULL | <gate><graph desc>
    <gate> = <gate id><gate input wires><gate output wires>
*/
std::pair<box_set, FUNC_ID>
load_code(const char *path) {
    auto code = read_code(path);
    std::map<FUNC_ID, std::shared_ptr<Box>> id_to_box = set_up();
    box_set boxes;

    FUNC_ID main_id = __4bytes_to_int(&code[0]);
    int offset = sizeof(FUNC_ID);

    auto skip_gate = [&](int it) -> int {
        FUNC_ID id = __4bytes_to_int(&code[it]);
        assert(id != POWER_PIN_ID);
        std::shared_ptr<Box> box = id_to_box[id];

        return it + sizeof(FUNC_ID) + (box->inputs_sz + box->outputs_sz) * sizeof(WIRE_ID);
    };

    auto skip_const = [&](int it) -> int {
        FUNC_ID id = __4bytes_to_int(&code[it]);
        assert(id == POWER_PIN_ID);
        it += sizeof(FUNC_ID);
        TYPE_ID type_id = code[it];
        it += sizeof(TYPE_ID);
        auto val_len = read_const_value(type_id, &code[it]);
        it += val_len.second;
        it += sizeof(WIRE_ID);

        return it;
    };

    // finding box definitions
    for(int it=offset ; it<code.size() ; ) { 
        int next = it;
        auto box = std::make_shared<Box>(false, 0, 0, 0);
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
        it ++;

        box->locals_sz = code[it];
        it += 1 + code[it] * sizeof(WIRE_ID);

        it = next;
    }

    std::map<WIRE_ID, Pin> env;

    for(int it=offset ; it<code.size() ; ) {
        int next = it;
        FUNC_ID box_id = __4bytes_to_int(&code[it]);
        std::shared_ptr<Box> box = id_to_box[box_id];
        std::unique_ptr<Graph> graph(new Graph());
        it += sizeof(FUNC_ID);

        next += __4bytes_to_int(&code[it]);
        it += sizeof(FUNC_LENGTH);

        // extracting sources, sinks and initials (consts and locals)
        {
            it ++; // inputs_sz byte
            for(int i=0 ; i<box->inputs_sz ; i++) {
                std::shared_ptr<Node> node = std::make_shared<Node>(__in_pin);
                graph->add_node(node, true);
                WIRE_ID wire = __4bytes_to_int(&code[it]);
                env[wire] = Pin(node, 0);
                it += sizeof(WIRE_ID);
            }
            it ++; // outputs_sz byte

            it ++; // locals_sz byte
            for(int i=0 ; i<box->locals_sz ; i++) {
                std::shared_ptr<Node> node = std::make_shared<Node>(__power_pin);
                graph->add_node(node);
                WIRE_ID wire = __4bytes_to_int(&code[it]);
                env[wire] = Pin(node, 0);
                graph->initials.push_back({env[wire], (PRIMITIVE_PTR)NULL});
                it += sizeof(WIRE_ID);
            }

            int ret_it = it;
            while(it < next) {
                FUNC_ID gate_id = __4bytes_to_int(&code[it]);
                if(gate_id != POWER_PIN_ID) {
                    it = skip_gate(it);
                    continue;
                }
                // std::shared_ptr<Box> box = id_to_box[gate_id];
                it += sizeof(FUNC_ID);

                TYPE_ID type_id = code[it];
                it += sizeof(TYPE_ID);
                std::shared_ptr<Node> node = std::make_shared<Node>(__power_pin);
                graph->add_node(node);
                auto val_len = read_const_value(type_id, &code[it]);
                it += val_len.second;
                WIRE_ID wire = __4bytes_to_int(&code[it]);
                env[wire] = Pin(node, 0);
                graph->initials.push_back({env[wire], val_len.first});
                it += sizeof(WIRE_ID);
            }

            it = ret_it;
        }

        while(it < next) {
            FUNC_ID gate_id = __4bytes_to_int(&code[it]);
            if(gate_id == POWER_PIN_ID) {
                it = skip_const(it);

                continue;
            }

            if(gate_id == OUT_PIN_ID) {
                std::shared_ptr<Node> node = std::make_shared<Node>(__out_pin);
                graph->add_node(node, false, true);
                it += sizeof(FUNC_ID);

                WIRE_ID wire_id = __4bytes_to_int(&code[it]);
                it += sizeof(WIRE_ID);

                Pin output_pin = env[wire_id];
                output_pin.first->out[ output_pin.second ].push_back({node, 0});

                continue;
            }

            std::shared_ptr<Box> box = id_to_box[gate_id];
            it += sizeof(FUNC_ID);
            std::shared_ptr<Node> node = std::make_shared<Node>(box);

            for(int i=0 ; i<box->inputs_sz ; i++) {
                WIRE_ID wire_id = __4bytes_to_int(&code[it]);
                it += sizeof(WIRE_ID);
                Pin output_pin = env[wire_id];
                Pin input_pin = Pin(node, i);
                output_pin.first->out[ output_pin.second ].push_back(input_pin);
            }

            for(int i=0 ; i<box->outputs_sz ; i++) {
                WIRE_ID wire_id = __4bytes_to_int(&code[it]);
                it += sizeof(WIRE_ID);
                Pin output_pin = Pin(node, i);
                env[wire_id] = output_pin;
            }
        }

        box->graph = std::move(graph);
        boxes.push_back(box);

        it = next;
    }

    return {boxes, main_id};
}