cmake_minimum_required(VERSION 3.10)
project(gomoku_engine)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Create a shared library target
add_library(gomoku SHARED
    src/backend/gomoku_engine.cpp
    src/backend/gomoku_wrapper.cpp
)

target_include_directories(gomoku PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/backend
)

# Set output name of library with proper prefix and suffix for different platforms
if(APPLE)
    set_target_properties(gomoku PROPERTIES PREFIX "lib" SUFFIX ".dylib")
elseif(UNIX AND NOT APPLE)
    set_target_properties(gomoku PROPERTIES PREFIX "lib" SUFFIX ".so")
elseif(WIN32)
    set_target_properties(gomoku PROPERTIES PREFIX "" SUFFIX ".dll")
endif()

# Install rules
install(TARGETS gomoku DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/lib)
