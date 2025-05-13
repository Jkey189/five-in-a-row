#ifndef GOMOKU_ENGINE_H
#define GOMOKU_ENGINE_H

#include <vector>
#include <cstdint>
#include <algorithm>
#include <climits>
#include <utility>
#include <stack>

// Move structure to track game history
struct Move {
    int row;
    int col;
    int player;
};

class GomokuEngine {
public:
    static const int BOARD_SIZE = 15;
    static const int EMPTY = 0;
    static const int PLAYER = 1;
    static const int AI = 2;
    
    enum Difficulty {
        EASY = 1,
        MEDIUM = 3,
        HARD = 5
    };
    
    // Constructor
    GomokuEngine();
    
    // Reset the game to initial state
    void resetGame();
    
    // Make a move at the specified position
    bool makeMove(int row, int col, int player);
    
    // Get the best move using alpha-beta pruning algorithm
    std::pair<int, int> getBestMove();
    
    // Set difficulty level (affects search depth)
    void setDifficulty(Difficulty level);
    
    // Get current difficulty level
    Difficulty getDifficulty() const;
    
    // Undo the last two moves (player and AI)
    bool undoMove();
    
    // Check if undo is possible
    bool canUndo() const;
    
    // Check if the game is over
    bool isGameOver() const;
    
    // Get the winner of the game (0 for no winner, 1 for player, 2 for AI)
    int getWinner() const;
    
    // Get the board state
    const std::vector<std::vector<int>>& getBoard() const;
    
private:
    std::vector<std::vector<int>> board;
    bool gameOver;
    int winner;
    Difficulty difficulty;
    std::stack<Move> moveHistory;
    
    // Alpha-beta pruning algorithm
    int alphaBetaPruning(int depth, int alpha, int beta, bool maximizingPlayer);
    
    // Evaluate the board state
    int evaluateBoard() const;
    
    // Helper function to evaluate a sequence of 5 positions
    int evaluateSequence(int aiCount, int playerCount) const;
    
    // Check if there are 5 stones in a row
    bool checkWin(int row, int col, int player) const;
    
    // Generate possible moves
    std::vector<std::pair<int, int>> generateMoves() const;
    
    // Check if a position is valid
    bool isValidPosition(int row, int col) const;
    
    // Check if a move has neighbors
    bool hasNeighbors(int row, int col) const;
};

#endif // GOMOKU_ENGINE_H