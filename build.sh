#!/bin/bash

# Create build directory
mkdir -p build
cd build

# Generate build files with CMake
cmake ..

# Build the project
make

# Create lib directory if it doesn't exist
mkdir -p ../lib

# Copy the library to the lib directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    cp libgomoku.dylib ../lib/
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp libgomoku.so ../lib/
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
    cp gomoku.dll ../lib/
fi

echo "Build completed successfully!"
