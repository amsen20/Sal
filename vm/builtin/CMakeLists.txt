project(builtin)

add_library(builtin builtin.cpp)

target_link_libraries(builtin prestate)