#include "gomoku_engine.h"

// Define static constants
const int GomokuEngine::BOARD_SIZE;
const int GomokuEngine::EMPTY;
const int GomokuEngine::PLAYER;
const int GomokuEngine::AI;

// Constructor
GomokuEngine::GomokuEngine() {
    resetGame();
    difficulty = MEDIUM; // Default difficulty
}

// Reset the game to initial state
void GomokuEngine::resetGame() {
    board = std::vector<std::vector<int>>(BOARD_SIZE, std::vector<int>(BOARD_SIZE, EMPTY));
    gameOver = false;
    winner = EMPTY;
    
    // Clear the move history
    while (!moveHistory.empty()) {
        moveHistory.pop();
    }
}

// Set difficulty level
void GomokuEngine::setDifficulty(Difficulty level) {
    difficulty = level;
}

// Get current difficulty level
GomokuEngine::Difficulty GomokuEngine::getDifficulty() const {
    return difficulty;
}

// Undo the last move
bool GomokuEngine::undoMove() {
    // Make sure there's at least one move to undo
    if (moveHistory.empty()) {
        return false;
    }
    
    // For player vs AI, we undo two moves (player's and AI's)
    for (int i = 0; i < 2; ++i) {
        if (moveHistory.empty()) {
            break;
        }
        
        // Get the last move
        Move lastMove = moveHistory.top();
        moveHistory.pop();
        
        // Clear that position
        board[lastMove.row][lastMove.col] = EMPTY;
    }
    
    // Reset game state if it was over
    if (gameOver) {
        gameOver = false;
        winner = EMPTY;
    }
    
    return true;
}

// Check if undo is possible
bool GomokuEngine::canUndo() const {
    return !moveHistory.empty();
}

// Make a move at the specified position
bool GomokuEngine::makeMove(int row, int col, int player) {
    if (!isValidPosition(row, col) || board[row][col] != EMPTY || gameOver) {
        return false;
    }
    
    board[row][col] = player;
    
    // Record this move in the history
    Move move = {row, col, player};
    moveHistory.push(move);
    
    // Check if the move results in a win
    if (checkWin(row, col, player)) {
        gameOver = true;
        winner = player;
    }
    
    return true;
}

// Get the best move using alpha-beta pruning algorithm
std::pair<int, int> GomokuEngine::getBestMove() {
    int bestScore = INT_MIN;
    std::pair<int, int> bestMove = {-1, -1};
    
    auto moves = generateMoves();
    if (moves.empty()) {
        // If board is empty, place in the center
        if (board[BOARD_SIZE/2][BOARD_SIZE/2] == EMPTY) {
            return {BOARD_SIZE/2, BOARD_SIZE/2};
        }
    }
    
    for (const auto& move : moves) {
        int row = move.first;
        int col = move.second;
        
        // Try this move
        board[row][col] = AI;
        
        // Evaluate the move with alpha-beta pruning using current difficulty level
        int score = alphaBetaPruning(static_cast<int>(difficulty), INT_MIN, INT_MAX, false);
        
        // Undo the move
        board[row][col] = EMPTY;
        
        // Update the best move if needed
        if (score > bestScore) {
            bestScore = score;
            bestMove = move;
        }
    }
    
    return bestMove;
}

// Check if the game is over
bool GomokuEngine::isGameOver() const {
    return gameOver;
}

// Get the winner of the game
int GomokuEngine::getWinner() const {
    return winner;
}

// Get the board state
const std::vector<std::vector<int>>& GomokuEngine::getBoard() const {
    return board;
}

// Alpha-beta pruning algorithm
int GomokuEngine::alphaBetaPruning(int depth, int alpha, int beta, bool maximizingPlayer) {
    // Check if the game is over or we've reached the maximum depth
    if (depth == 0 || gameOver) {
        return evaluateBoard();
    }
    
    auto moves = generateMoves();
    
    if (maximizingPlayer) {
        int maxEval = INT_MIN;
        for (const auto& move : moves) {
            int row = move.first;
            int col = move.second;
            
            // Try this move
            board[row][col] = AI;
            
            // Evaluate the move
            int eval = alphaBetaPruning(depth - 1, alpha, beta, false);
            
            // Undo the move
            board[row][col] = EMPTY;
            
            maxEval = std::max(maxEval, eval);
            alpha = std::max(alpha, eval);
            if (beta <= alpha) {
                break; // Beta cut-off
            }
        }
        return maxEval;
    } else {
        int minEval = INT_MAX;
        for (const auto& move : moves) {
            int row = move.first;
            int col = move.second;
            
            // Try this move
            board[row][col] = PLAYER;
            
            // Evaluate the move
            int eval = alphaBetaPruning(depth - 1, alpha, beta, true);
            
            // Undo the move
            board[row][col] = EMPTY;
            
            minEval = std::min(minEval, eval);
            beta = std::min(beta, eval);
            if (beta <= alpha) {
                break; // Alpha cut-off
            }
        }
        return minEval;
    }
}

// Evaluate the board state
int GomokuEngine::evaluateBoard() const {
    int score = 0;
    
    // Check rows
    for (int row = 0; row < BOARD_SIZE; ++row) {
        for (int col = 0; col < BOARD_SIZE - 4; ++col) {
            int aiCount = 0;
            int playerCount = 0;
            
            for (int i = 0; i < 5; ++i) {
                if (board[row][col + i] == AI) ++aiCount;
                else if (board[row][col + i] == PLAYER) ++playerCount;
            }
            
            score += evaluateSequence(aiCount, playerCount);
        }
    }
    
    // Check columns
    for (int col = 0; col < BOARD_SIZE; ++col) {
        for (int row = 0; row < BOARD_SIZE - 4; ++row) {
            int aiCount = 0;
            int playerCount = 0;
            
            for (int i = 0; i < 5; ++i) {
                if (board[row + i][col] == AI) ++aiCount;
                else if (board[row + i][col] == PLAYER) ++playerCount;
            }
            
            score += evaluateSequence(aiCount, playerCount);
        }
    }
    
    // Check diagonals (top-left to bottom-right)
    for (int row = 0; row < BOARD_SIZE - 4; ++row) {
        for (int col = 0; col < BOARD_SIZE - 4; ++col) {
            int aiCount = 0;
            int playerCount = 0;
            
            for (int i = 0; i < 5; ++i) {
                if (board[row + i][col + i] == AI) ++aiCount;
                else if (board[row + i][col + i] == PLAYER) ++playerCount;
            }
            
            score += evaluateSequence(aiCount, playerCount);
        }
    }
    
    // Check diagonals (top-right to bottom-left)
    for (int row = 0; row < BOARD_SIZE - 4; ++row) {
        for (int col = 4; col < BOARD_SIZE; ++col) {
            int aiCount = 0;
            int playerCount = 0;
            
            for (int i = 0; i < 5; ++i) {
                if (board[row + i][col - i] == AI) ++aiCount;
                else if (board[row + i][col - i] == PLAYER) ++playerCount;
            }
            
            score += evaluateSequence(aiCount, playerCount);
        }
    }
    
    return score;
}

// Helper function to evaluate a sequence of 5 positions
int GomokuEngine::evaluateSequence(int aiCount, int playerCount) const {
    // If both AI and player have stones, this sequence is not interesting
    if (aiCount > 0 && playerCount > 0) return 0;
    
    // Score for AI sequences
    if (aiCount > 0) {
        if (aiCount == 5) return 100000; // Win
        if (aiCount == 4) return 10000;  // Open four
        if (aiCount == 3) return 1000;   // Open three
        if (aiCount == 2) return 100;    // Open two
        if (aiCount == 1) return 10;     // Single stone
    }
    
    // Score for player sequences (negative to minimize)
    if (playerCount > 0) {
        if (playerCount == 5) return -100000; // Loss
        if (playerCount == 4) return -10000;  // Block open four
        if (playerCount == 3) return -1000;   // Block open three
        if (playerCount == 2) return -100;    // Block open two
        if (playerCount == 1) return -10;     // Single stone
    }
    
    return 0;
}

// Check if there are 5 stones in a row
bool GomokuEngine::checkWin(int row, int col, int player) const {
    // Check horizontally
    int count = 0;
    for (int c = std::max(0, col - 4); c <= std::min(BOARD_SIZE - 1, col + 4); ++c) {
        if (board[row][c] == player) {
            count++;
            if (count >= 5) return true;
        } else {
            count = 0;
        }
    }
    
    // Check vertically
    count = 0;
    for (int r = std::max(0, row - 4); r <= std::min(BOARD_SIZE - 1, row + 4); ++r) {
        if (board[r][col] == player) {
            count++;
            if (count >= 5) return true;
        } else {
            count = 0;
        }
    }
    
    // Check diagonal (top-left to bottom-right)
    count = 0;
    for (int i = -4; i <= 4; ++i) {
        int r = row + i;
        int c = col + i;
        if (r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE) {
            if (board[r][c] == player) {
                count++;
                if (count >= 5) return true;
            } else {
                count = 0;
            }
        }
    }
    
    // Check diagonal (top-right to bottom-left)
    count = 0;
    for (int i = -4; i <= 4; ++i) {
        int r = row + i;
        int c = col - i;
        if (r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE) {
            if (board[r][c] == player) {
                count++;
                if (count >= 5) return true;
            } else {
                count = 0;
            }
        }
    }
    
    return false;
}

// Generate possible moves
std::vector<std::pair<int, int>> GomokuEngine::generateMoves() const {
    std::vector<std::pair<int, int>> moves;
    
    // Check all empty cells that have at least one neighbor
    for (int row = 0; row < BOARD_SIZE; ++row) {
        for (int col = 0; col < BOARD_SIZE; ++col) {
            if (board[row][col] == EMPTY && hasNeighbors(row, col)) {
                moves.push_back({row, col});
            }
        }
    }
    
    // If no moves found, the board is empty or all stones are isolated
    if (moves.empty()) {
        for (int row = 0; row < BOARD_SIZE; ++row) {
            for (int col = 0; col < BOARD_SIZE; ++col) {
                if (board[row][col] == EMPTY) {
                    moves.push_back({row, col});
                }
            }
        }
    }
    
    return moves;
}

// Check if a position is valid
bool GomokuEngine::isValidPosition(int row, int col) const {
    return row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE;
}

// Check if a move has neighbors
bool GomokuEngine::hasNeighbors(int row, int col) const {
    // Check all 8 directions
    for (int dr = -1; dr <= 1; ++dr) {
        for (int dc = -1; dc <= 1; ++dc) {
            if (dr == 0 && dc == 0) continue; // Skip the center
            
            int r = row + dr;
            int c = col + dc;
            if (isValidPosition(r, c) && board[r][c] != EMPTY) {
                return true;
            }
        }
    }
    
    return false;
}
