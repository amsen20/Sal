project(loader)

add_library(loader loader.cpp)

target_link_libraries(loader prestate)
target_link_libraries(loader utils)