cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(ctre CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ctre::ctre)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD_REQUIRED ON)
