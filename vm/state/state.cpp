#include "state.h"

std::shared_ptr<prestate::Box>
state::Node::get_box() {
    return this->prenode->box;
}
