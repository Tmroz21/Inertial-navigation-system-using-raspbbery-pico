cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(test_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()
add_executable(inertial_navigation
  main.c
)
pico_enable_stdio_usb(inertial_navigation 1)
pico_enable_stdio_uart(inertial_navigation 1)
pico_add_extra_outputs(inertial_navigation)
target_link_libraries(inertial_navigation pico_stdlib)