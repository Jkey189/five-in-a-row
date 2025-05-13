#!/usr/bin/env python3

"""
Simple test script to verify the C++ backend is working correctly.
This doesn't use any GUI - it just tests the basic functionality of the game engine.
"""

import sys
import os
import ctypes
from ctypes import c_void_p, c_int, POINTER, byref
import time

def main():
    print("Five in a Row (Gomoku) Backend Test")
    print("-----------------------------------")
    
    # Load the shared library
    if sys.platform.startswith('darwin'):  # macOS
        # Try several possible library locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib/libgomoku.dylib'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib/libgomoku.dylib'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build/libgomoku.dylib')
        ]
        lib_path = None
        for path in possible_paths:
            if os.path.exists(path):
                lib_path = path
                break
        if not lib_path:
            lib_path = possible_paths[0]  # Default path for error reporting
    elif sys.platform.startswith('linux'):  # Linux
        # Try several possible library locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib/libgomoku.so'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib/libgomoku.so'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build/libgomoku.so')
        ]
        lib_path = None
        for path in possible_paths:
            if os.path.exists(path):
                lib_path = path
                break
        if not lib_path:
            lib_path = possible_paths[0]  # Default path for error reporting
    elif sys.platform.startswith('win'):  # Windows
        # Try several possible library locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib/gomoku.dll'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib/gomoku.dll'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build/Release/gomoku.dll'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build/gomoku.dll')
        ]
        lib_path = None
        for path in possible_paths:
            if os.path.exists(path):
                lib_path = path
                break
        if not lib_path:
            lib_path = possible_paths[0]  # Default path for error reporting
    else:
        raise OSError("Unsupported platform")
    
    print(f"Loading library from: {lib_path}")
    try:
        lib = ctypes.CDLL(lib_path)
        print("Library loaded successfully!")
    except OSError as e:
        print(f"Error loading library: {e}")
        print("\nTrying alternative locations...")
        
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try build directory
        if sys.platform.startswith('darwin'):
            alt_path = os.path.join(project_root, 'build', 'libgomoku.dylib')
        elif sys.platform.startswith('linux'):
            alt_path = os.path.join(project_root, 'build', 'libgomoku.so')
        else:  # Windows
            alt_path = os.path.join(project_root, 'build', 'gomoku.dll')
            if not os.path.exists(alt_path):
                alt_path = os.path.join(project_root, 'build', 'Release', 'gomoku.dll')
        
        print(f"Trying: {alt_path}")
        try:
            lib = ctypes.CDLL(alt_path)
            print("Library loaded from alternative location!")
        except OSError as e2:
            print(f"Error loading from alternative location: {e2}")
            print("\nMake sure you've built the C++ backend by running build.sh or build.bat")
            return 1
    
    # Define constants
    EMPTY = 0
    PLAYER = 1
    AI = 2
    BOARD_SIZE = 15
    
    # Define function prototypes
    lib.create_engine.restype = c_void_p
    lib.destroy_engine.argtypes = [c_void_p]
    lib.reset_game.argtypes = [c_void_p]
    lib.make_move.argtypes = [c_void_p, c_int, c_int, c_int]
    lib.make_move.restype = c_int
    lib.get_best_move.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    lib.is_game_over.argtypes = [c_void_p]
    lib.is_game_over.restype = c_int
    lib.get_winner.argtypes = [c_void_p]
    lib.get_winner.restype = c_int
    lib.get_board_value.argtypes = [c_void_p, c_int, c_int]
    lib.get_board_value.restype = c_int
    
    # Create an engine instance
    print("Creating engine...")
    engine = lib.create_engine()
    print("Engine created!")
    
    # Test basic functionality
    print("\nTesting reset game...")
    lib.reset_game(engine)
    print("Game reset!")
    
    print("\nTesting make move...")
    result = lib.make_move(engine, 7, 7, PLAYER)
    print(f"Make move result: {result}")
    
    board_value = lib.get_board_value(engine, 7, 7)
    print(f"Board value at (7,7): {board_value}")
    
    print("\nTesting AI move generation...")
    print("Computing best move (this might take a moment)...")
    start_time = time.time()
    row = c_int()
    col = c_int()
    lib.get_best_move(engine, byref(row), byref(col))
    elapsed = time.time() - start_time
    print(f"AI chose move: ({row.value}, {col.value}) in {elapsed:.2f} seconds")
    
    # Make the AI move
    lib.make_move(engine, row.value, col.value, AI)
    
    # Print the board
    print("\nCurrent board state:")
    for i in range(BOARD_SIZE):
        row_str = ""
        for j in range(BOARD_SIZE):
            value = lib.get_board_value(engine, i, j)
            if value == EMPTY:
                row_str += ". "
            elif value == PLAYER:
                row_str += "X "
            elif value == AI:
                row_str += "O "
        print(row_str)
    
    # Check game status
    game_over = lib.is_game_over(engine)
    winner = lib.get_winner(engine)
    print(f"\nGame over: {bool(game_over)}")
    print(f"Winner: {winner}")
    
    # Clean up
    print("\nCleaning up...")
    lib.destroy_engine(engine)
    print("Engine destroyed!")
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
