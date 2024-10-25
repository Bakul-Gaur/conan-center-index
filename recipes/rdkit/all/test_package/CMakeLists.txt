cmake_minimum_required(VERSION 3.24)

project(test_rdkit LANGUAGES CXX)

find_package(rdkit REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_rdkit.cpp)

target_link_libraries(${PROJECT_NAME}
                      PRIVATE rdkit::rdkit_shared
)

# Boost include path fix (It's unclear why CMake doesn't set Boost include dir automatically in the build command when
# I run `conan create` inside a docker container, even if I specify `Boost::headers` or `boost::boost` above. To be
# debugged.):
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_INCLUDE_PATH})

# TODO: figure out how to test case `rdkit::rdkit_static`. It's not trivial and it may not work everywhere. E.g., see
# discussion here: https://github.com/conan-io/conan/issues/6530
