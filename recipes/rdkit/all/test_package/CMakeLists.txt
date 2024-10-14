cmake_minimum_required(VERSION 3.24)

project(test_rdkit LANGUAGES CXX)

find_package(rdkit REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_rdkit.cpp)

target_link_libraries(${PROJECT_NAME}
                      PRIVATE rdkit::rdkit_shared
)

# TODO: figure out how to test case `rdkit::rdkit_static`. It's not trivial and it may not work everywhere. E.g., see
# discussion here: https://github.com/conan-io/conan/issues/6530
