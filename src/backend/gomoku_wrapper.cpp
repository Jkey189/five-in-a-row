#include "gomoku_wrapper.h"
#include "gomoku_engine.h"

// Create a new engine
void* create_engine() {
    return new GomokuEngine();
}

// Destroy the engine
void destroy_engine(void* engine) {
    delete static_cast<GomokuEngine*>(engine);
}

// Reset the game
void reset_game(void* engine) {
    static_cast<GomokuEngine*>(engine)->resetGame();
}

// Make a move
int make_move(void* engine, int row, int col, int player) {
    return static_cast<GomokuEngine*>(engine)->makeMove(row, col, player);
}

// Get the best move for AI
void get_best_move(void* engine, int* row, int* col) {
    auto move = static_cast<GomokuEngine*>(engine)->getBestMove();
    *row = move.first;
    *col = move.second;
}

// Check if the game is over
int is_game_over(void* engine) {
    return static_cast<GomokuEngine*>(engine)->isGameOver() ? 1 : 0;
}

// Get the winner
int get_winner(void* engine) {
    return static_cast<GomokuEngine*>(engine)->getWinner();
}

// Get the value at a specific board position
int get_board_value(void* engine, int row, int col) {
    const auto& board = static_cast<GomokuEngine*>(engine)->getBoard();
    if (row >= 0 && row < GomokuEngine::BOARD_SIZE && col >= 0 && col < GomokuEngine::BOARD_SIZE) {
        return board[row][col];
    }
    return -1;
}

// Set difficulty level
void set_difficulty(void* engine, int level) {
    GomokuEngine::Difficulty difficulty;
    
    // Map the numerical level to the enum
    if (level <= 1) {
        difficulty = GomokuEngine::EASY;
    } else if (level >= 5) {
        difficulty = GomokuEngine::HARD;
    } else {
        difficulty = GomokuEngine::MEDIUM;
    }
    
    static_cast<GomokuEngine*>(engine)->setDifficulty(difficulty);
}

// Get current difficulty level
int get_difficulty(void* engine) {
    GomokuEngine::Difficulty difficulty = static_cast<GomokuEngine*>(engine)->getDifficulty();
    return static_cast<int>(difficulty);
}

// Undo the last move(s)
int undo_move(void* engine) {
    return static_cast<GomokuEngine*>(engine)->undoMove() ? 1 : 0;
}

// Check if undo is possible
int can_undo(void* engine) {
    return static_cast<GomokuEngine*>(engine)->canUndo() ? 1 : 0;
}
