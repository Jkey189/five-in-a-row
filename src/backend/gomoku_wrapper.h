#ifndef GOMOKU_WRAPPER_H
#define GOMOKU_WRAPPER_H

#ifdef __cplusplus
extern "C" {
#endif

// Create a new engine
void* create_engine();

// Destroy the engine
void destroy_engine(void* engine);

// Reset the game
void reset_game(void* engine);

// Make a move
int make_move(void* engine, int row, int col, int player);

// Get the best move for AI
void get_best_move(void* engine, int* row, int* col);

// Check if the game is over
int is_game_over(void* engine);

// Get the winner
int get_winner(void* engine);

// Get the value at a specific board position
int get_board_value(void* engine, int row, int col);

// Set difficulty level (1 = Easy, 3 = Medium, 5 = Hard)
void set_difficulty(void* engine, int level);

// Get current difficulty level
int get_difficulty(void* engine);

// Undo the last move(s)
int undo_move(void* engine);

// Check if undo is possible
int can_undo(void* engine);

#ifdef __cplusplus
}
#endif

#endif // GOMOKU_WRAPPER_H
