project(vm)

add_library(vm vm.cpp)

target_link_libraries(vm prestate)