project(vm)

add_library(vm vm.cpp)

target_link_libraries(vm prestate)
target_link_libraries(vm state)
target_link_libraries(vm utils)