project(state)

add_library(state state.cpp)

target_link_libraries(state prestate)
target_link_libraries(state utils)