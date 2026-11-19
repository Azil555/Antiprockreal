cmake_minimum_required(VERSION 3.16)

project(pi_zero_project)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_custom_target(run_pi_zero_project
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/src/main.py
    USES_TERMINAL
)
