cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(turtle REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} turtle::turtle)
if(turtle_VERSION VERSION_GREATER_EQUAL "2.0.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
