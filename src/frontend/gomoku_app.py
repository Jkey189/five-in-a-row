import sys
import os
import ctypes
import json
import time
import platform
from ctypes import c_void_p, c_int, POINTER, byref
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
                           QLabel, QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox,
                           QGroupBox, QFrame, QAction, QFileDialog, QDialog, QTextBrowser,
                           QCheckBox)
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QRadialGradient, QIcon

class GomokuEngine:
    """Python wrapper for the C++ backend"""
    
    EMPTY = 0
    PLAYER = 1
    AI = 2
    BOARD_SIZE = 15
    
    # Difficulty constants
    EASY = 1
    MEDIUM = 3
    HARD = 5
    
    def __init__(self):
        # Load the shared library
        if sys.platform.startswith('darwin'):
            # On macOS, try several possible library locations
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
                # Default to the standard path and report the error later
                lib_path = possible_paths[0]
                print(f"Warning: Library not found in any of the expected locations. Will try: {lib_path}")
        elif sys.platform.startswith('linux'):
            lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib/libgomoku.so')
        elif sys.platform.startswith('win'):
            lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib/gomoku.dll')
        else:
            raise OSError("Unsupported platform")
        
        print(f"Attempting to load library from: {lib_path}")
        try:
            self.lib = ctypes.CDLL(lib_path)
            print("Library loaded successfully!")
        except OSError as e:
            print(f"Error loading library: {e}")
            print("Trying alternative methods to find the library...")
            
            # Try to locate the library in the build directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            build_lib_path = os.path.join(project_root, 'build', 'libgomoku.dylib')
            print(f"Trying: {build_lib_path}")
            
            try:
                self.lib = ctypes.CDLL(build_lib_path)
                print("Library loaded from build directory!")
            except OSError as e2:
                print(f"Failed to load from build directory: {e2}")
                raise e  # Re-raise the original exception
        
        # Define function prototypes
        self.lib.create_engine.restype = c_void_p
        self.lib.destroy_engine.argtypes = [c_void_p]
        self.lib.reset_game.argtypes = [c_void_p]
        self.lib.make_move.argtypes = [c_void_p, c_int, c_int, c_int]
        self.lib.make_move.restype = c_int
        self.lib.get_best_move.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.lib.is_game_over.argtypes = [c_void_p]
        self.lib.is_game_over.restype = c_int
        self.lib.get_winner.argtypes = [c_void_p]
        self.lib.get_winner.restype = c_int
        self.lib.get_board_value.argtypes = [c_void_p, c_int, c_int]
        self.lib.get_board_value.restype = c_int
        self.lib.set_difficulty.argtypes = [c_void_p, c_int]
        self.lib.get_difficulty.argtypes = [c_void_p]
        self.lib.get_difficulty.restype = c_int
        self.lib.undo_move.argtypes = [c_void_p]
        self.lib.undo_move.restype = c_int
        self.lib.can_undo.argtypes = [c_void_p]
        self.lib.can_undo.restype = c_int
        
        # Create an engine instance
        self.engine = self.lib.create_engine()
    
    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'engine'):
            self.lib.destroy_engine(self.engine)
    
    def reset_game(self):
        self.lib.reset_game(self.engine)
    
    def make_move(self, row, col, player):
        return bool(self.lib.make_move(self.engine, row, col, player))
    
    def get_best_move(self):
        row = c_int()
        col = c_int()
        self.lib.get_best_move(self.engine, byref(row), byref(col))
        return row.value, col.value
    
    def is_game_over(self):
        return bool(self.lib.is_game_over(self.engine))
    
    def get_winner(self):
        return self.lib.get_winner(self.engine)
    
    def get_board_value(self, row, col):
        return self.lib.get_board_value(self.engine, row, col)
    
    def set_difficulty(self, level):
        self.lib.set_difficulty(self.engine, level)
    
    def get_difficulty(self):
        return self.lib.get_difficulty(self.engine)
        
    def undo_move(self):
        return bool(self.lib.undo_move(self.engine))
    
    def can_undo(self):
        return bool(self.lib.can_undo(self.engine))


class BoardCell(QPushButton):
    """A cell in the Gomoku board"""
    
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.value = GomokuEngine.EMPTY
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #E0B879;
                border: none;
            }
            QPushButton:focus {
                border: 2px solid #FF5733;
            }
        """)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
    
    def set_value(self, value):
        self.value = value
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the grid lines
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        
        # Draw horizontal line - cast float to int to fix type error
        painter.drawLine(0, int(self.height() / 2), self.width(), int(self.height() / 2))
        
        # Draw vertical line - cast float to int to fix type error
        painter.drawLine(int(self.width() / 2), 0, int(self.width() / 2), self.height())
        
        # Check if this is an edge cell and only draw inner half of grid lines
        if self.row == 0:
            # First row only draws bottom half
            painter.drawLine(int(self.width() / 2), int(self.height() / 2), int(self.width() / 2), self.height())
        
        if self.row == GomokuEngine.BOARD_SIZE - 1:
            # Last row only draws top half
            painter.drawLine(int(self.width() / 2), 0, int(self.width() / 2), int(self.height() / 2))
            
        if self.col == 0:
            # First column only draws right half
            painter.drawLine(int(self.width() / 2), int(self.height() / 2), self.width(), int(self.height() / 2))
            
        if self.col == GomokuEngine.BOARD_SIZE - 1:
            # Last column only draws left half
            painter.drawLine(0, int(self.height() / 2), int(self.width() / 2), int(self.height() / 2))
        
        # Draw stone if not empty
        if self.value == GomokuEngine.PLAYER:
            # Black stone with subtle gradient
            gradient = QRadialGradient(15, 15, 20)
            gradient.setColorAt(0, QColor(50, 50, 50))
            gradient.setColorAt(1, QColor(0, 0, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(5, 5, 30, 30)
            
            # Add highlight to give 3D effect
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
            painter.drawEllipse(10, 10, 10, 10)
            
        elif self.value == GomokuEngine.AI:
            # White stone with subtle gradient
            gradient = QRadialGradient(15, 15, 20)
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(1, QColor(220, 220, 220))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawEllipse(5, 5, 30, 30)
            
            # Add highlight to give 3D effect
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
            painter.drawEllipse(10, 10, 15, 10)


class GomokuBoard(QWidget):
    """The Gomoku board widget"""
    
    # Signal to update the game timer
    move_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.engine = GomokuEngine()
        self.player_turn = True
        self.game_in_progress = False
        
        # Game statistics
        self.games_played = 0
        self.player_wins = 0
        self.ai_wins = 0
        self.draws = 0
        
        # For keyboard navigation
        self.setFocusPolicy(Qt.StrongFocus)
        self.current_focus = (7, 7)  # Center cell
    
    def init_ui(self):
        layout = QGridLayout()
        layout.setSpacing(0)
        
        self.cells = []
        for row in range(GomokuEngine.BOARD_SIZE):
            row_cells = []
            for col in range(GomokuEngine.BOARD_SIZE):
                cell = BoardCell(row, col)
                cell.clicked.connect(self.cell_clicked)
                layout.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        self.setLayout(layout)
    

            
    def reset_game(self):
        self.engine.reset_game()
        self.player_turn = True
        self.game_in_progress = True
        
        # Reset the UI
        for row in range(GomokuEngine.BOARD_SIZE):
            for col in range(GomokuEngine.BOARD_SIZE):
                self.cells[row][col].set_value(GomokuEngine.EMPTY)
        
        # Set focus to center cell
        self.current_focus = (GomokuEngine.BOARD_SIZE // 2, GomokuEngine.BOARD_SIZE // 2)
        self.cells[self.current_focus[0]][self.current_focus[1]].setFocus()
                
        # Update status if parent window exists
        if hasattr(self.parent(), 'update_status'):
            self.parent().update_status("Your turn (Black)")
        
        # Signal that a new game has started
        self.move_made.emit()
    
    def cell_clicked(self):
        if not self.player_turn or self.engine.is_game_over():
            return
        
        # Get the clicked cell
        cell = self.sender()
        row, col = cell.row, cell.col
        
        # Check if the cell is empty
        if self.engine.get_board_value(row, col) != GomokuEngine.EMPTY:
            return
        
        # Make player's move
        if self.engine.make_move(row, col, GomokuEngine.PLAYER):
            cell.set_value(GomokuEngine.PLAYER)
            
            # Signal that a move was made
            self.move_made.emit()
            
            # Update status if parent exists
            if hasattr(self.parent(), 'update_status'):
                self.parent().update_status("AI is thinking...")
            
            # Check if game over
            if self.engine.is_game_over():
                self.game_over()
                return
            
            # AI's turn
            self.player_turn = False
            self.ai_move()
    
    def ai_move(self):
        # Get AI's move
        row, col = self.engine.get_best_move()
        
        # Make AI's move
        if row >= 0 and col >= 0:
            if self.engine.make_move(row, col, GomokuEngine.AI):
                self.cells[row][col].set_value(GomokuEngine.AI)
                
                # Signal that a move was made
                self.move_made.emit()
        
        # Check if game over
        if self.engine.is_game_over():
            self.game_over()
            return
        
        # Player's turn
        self.player_turn = True
        
        # Update status if parent exists
        if hasattr(self.parent(), 'update_status'):
            self.parent().update_status("Your turn (Black)")
    
    def game_over(self):
        winner = self.engine.get_winner()
        message = ""
        
        # Update game statistics
        self.games_played += 1
        self.game_in_progress = False
        
        if winner == GomokuEngine.PLAYER:
            message = "Congratulations! You win!"
            self.player_wins += 1
                
        elif winner == GomokuEngine.AI:
            message = "AI wins! Better luck next time."
            self.ai_wins += 1
                
        else:
            message = "It's a draw!"
            self.draws += 1
        
        # Update status if parent exists
        if hasattr(self.parent(), 'update_status'):
            self.parent().update_status(message)
        
        # Notify parent to update statistics display
        if hasattr(self.parent(), 'update_statistics'):
            self.parent().update_statistics(self.games_played, self.player_wins, self.ai_wins, self.draws)
        
        reply = QMessageBox.question(self, 'Game Over', 
            f"{message} Do you want to play again?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.reset_game()
            
    def set_difficulty(self, difficulty):
        """Set the difficulty level of the AI"""
        self.engine.set_difficulty(difficulty)
        
    def undo_last_move(self):
        """Undo the last moves (player and AI)"""
        if self.engine.can_undo() and self.game_in_progress and self.player_turn:
            if self.engine.undo_move():
                # Update the UI to reflect the change
                for row in range(GomokuEngine.BOARD_SIZE):
                    for col in range(GomokuEngine.BOARD_SIZE):
                        value = self.engine.get_board_value(row, col)
                        self.cells[row][col].set_value(value)
                return True
        return False
    
    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if not self.game_in_progress or not self.player_turn:
            return super().keyPressEvent(event)
            
        row, col = self.current_focus
            
        # Arrow keys for navigation
        if event.key() == Qt.Key_Up and row > 0:
            row -= 1
        elif event.key() == Qt.Key_Down and row < GomokuEngine.BOARD_SIZE - 1:
            row += 1
        elif event.key() == Qt.Key_Left and col > 0:
            col -= 1
        elif event.key() == Qt.Key_Right and col < GomokuEngine.BOARD_SIZE - 1:
            col += 1
        # Enter or Space to make a move
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            # Simulate a click on the cell
            if self.engine.get_board_value(row, col) == GomokuEngine.EMPTY:
                cell = self.cells[row][col]
                cell.click()
                return
        # U to undo
        elif event.key() == Qt.Key_U:
            self.undo_last_move()
            return
        else:
            return super().keyPressEvent(event)
            
        # Update focus
        self.current_focus = (row, col)
        self.cells[row][col].setFocus()
        
    def find_resource(self, filename, resource_dirs):
        """Find a resource file in multiple possible directories"""
        # First check all provided directories
        for directory in resource_dirs:
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                return filepath
                
        # If the file was not found, return the path in the first directory
        # (it will be created there if needed)
        return os.path.join(resource_dirs[0], filename)
        
    def get_board_state(self):
        """Get the current state of the board as a 2D array"""
        board = []
        for row in range(GomokuEngine.BOARD_SIZE):
            board_row = []
            for col in range(GomokuEngine.BOARD_SIZE):
                board_row.append(self.engine.get_board_value(row, col))
            board.append(board_row)
        return board


class GomokuWindow(QMainWindow):
    """Main window for the Gomoku game"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_menu()
        self.init_timer()
        self.load_settings()
        self.setup_icon()
        
        # Display version info in the status bar
        version = "1.0.0"  # Update this with the correct version number
        platform_name = platform.system()
        python_version = platform.python_version()
        self.statusBar().showMessage(f"Ready | Five in a Row v{version} | {platform_name} | Python {python_version}")
        
        self.show()
        
        # Validate that everything is loaded correctly
        self._validate_environment()
        
    def _validate_environment(self):
        """Validate that all required components are available"""
        issues = []
        
        # Check that the C++ library was loaded
        if not hasattr(self.board, 'engine') or not hasattr(self.board.engine, 'lib'):
            issues.append("Failed to load the C++ backend library")
        
        # Check for required resources
        resource_files = ['gomoku_icon.png']
        missing_resources = []
        
        # Check multiple resource directories
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_resource_dirs = [
            os.path.join(project_root, 'resources'),
            os.path.join(project_root, 'src', 'resources'),
            os.path.join(project_root, '..', 'resources')
        ]
        
        for resource in resource_files:
            found = False
            for dir_path in possible_resource_dirs:
                if os.path.exists(os.path.join(dir_path, resource)):
                    found = True
                    break
            if not found:
                missing_resources.append(resource)
        
        if missing_resources:
            issues.append(f"Missing resources: {', '.join(missing_resources)}")
        
        # Report any issues
        if issues:
            warning_msg = "The following issues were detected:\n\n" + "\n".join(issues)
            warning_msg += "\n\nThe game may not function correctly. Please run the setup script to fix these issues."
            QMessageBox.warning(self, "Environment Issues", warning_msg)
    
    def init_ui(self):
        self.setWindowTitle('Five in a Row (Gomoku)')
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left side - Game panel and controls
        left_panel = QVBoxLayout()
        
        # Create header with status and game info
        header_layout = QHBoxLayout()
        
        # Game status
        status_box = QHBoxLayout()
        self.status_label = QLabel("Ready to play")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_box.addWidget(self.status_label)
        
        # Game timer
        self.timer_label = QLabel("Time: 00:00")
        self.timer_label.setStyleSheet("font-size: 14px;")
        status_box.addWidget(self.timer_label)
        
        header_layout.addLayout(status_box)
        
        # Game controls
        controls_box = QHBoxLayout()
        
        # New Game button
        self.reset_btn = QPushButton("New Game")
        self.reset_btn.clicked.connect(self.reset_game)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        controls_box.addWidget(self.reset_btn)
        
        # Undo button
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_move)
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.undo_btn.setEnabled(False)  # Initially disabled
        controls_box.addWidget(self.undo_btn)
        
        header_layout.addLayout(controls_box)
        
        left_panel.addLayout(header_layout)
        
        # Create the board
        self.board = GomokuBoard(self)
        self.board.move_made.connect(self.on_move_made)
        left_panel.addWidget(self.board)
        
        main_layout.addLayout(left_panel, 7)  # Board takes 70% of width
        
        # Right side - Controls and statistics
        right_panel = QVBoxLayout()
        
        # Difficulty selector
        difficulty_group = QGroupBox("AI Difficulty")
        difficulty_layout = QVBoxLayout()
        
        self.difficulty_selector = QComboBox()
        self.difficulty_selector.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_selector.setCurrentIndex(1)  # Default to Medium
        self.difficulty_selector.currentIndexChanged.connect(self.change_difficulty)
        
        difficulty_layout.addWidget(self.difficulty_selector)
        difficulty_group.setLayout(difficulty_layout)
        right_panel.addWidget(difficulty_group)
        
        # Game options
        options_group = QGroupBox("Game Options")
        options_layout = QVBoxLayout()
        
        # Add any future options here
        
        options_group.setLayout(options_layout)
        right_panel.addWidget(options_group)
        
        # Game statistics
        stats_group = QGroupBox("Game Statistics")
        stats_layout = QVBoxLayout()
        
        self.games_played_label = QLabel("Games Played: 0")
        self.player_wins_label = QLabel("Your Wins: 0")
        self.ai_wins_label = QLabel("AI Wins: 0")
        self.draws_label = QLabel("Draws: 0")
        self.win_rate_label = QLabel("Win Rate: 0%")
        
        stats_layout.addWidget(self.games_played_label)
        stats_layout.addWidget(self.player_wins_label)
        stats_layout.addWidget(self.ai_wins_label)
        stats_layout.addWidget(self.draws_label)
        stats_layout.addWidget(self.win_rate_label)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        stats_layout.addWidget(separator)
        
        # Tip and help text
        tip_label = QLabel("Tip: Connect five stones in a row to win!")
        tip_label.setWordWrap(True)
        stats_layout.addWidget(tip_label)
        
        # Keyboard shortcuts help
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout()
        
        shortcuts_text = """
        • Arrow keys: Navigate board
        • Space/Enter: Place stone
        • U: Undo move
        • Ctrl+N: New game
        • Ctrl+S: Save game
        • Ctrl+O: Load game
        • Ctrl+Z: Undo move
        • Ctrl+Q: Quit
        """
        
        shortcuts_label = QLabel(shortcuts_text)
        shortcuts_label.setWordWrap(True)
        shortcuts_layout.addWidget(shortcuts_label)
        
        shortcuts_group.setLayout(shortcuts_layout)
        stats_layout.addWidget(shortcuts_group)
        
        stats_group.setLayout(stats_layout)
        right_panel.addWidget(stats_group)
        
        # Add spacing at the bottom of the right panel
        right_panel.addStretch(1)
        
        main_layout.addLayout(right_panel, 3)  # Controls take 30% of width
        
        # Set window properties with an elegant color scheme
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #2C3E50; 
                color: #ECF0F1;
            }
            QWidget { 
                background-color: #2C3E50; 
                color: #ECF0F1;
            }
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #34495E; 
                border-radius: 5px; 
                margin-top: 10px; 
                background-color: #34495E;
                color: #ECF0F1;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px 0 5px; 
                color: #3498DB;
            }
            QLabel { 
                padding: 5px; 
                color: #ECF0F1;
            }
            QComboBox { 
                padding: 5px; 
                background-color: #34495E; 
                color: #ECF0F1;
                border: 1px solid #3498DB;
                border-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #2980B9;
            }
            QComboBox QAbstractItemView {
                background-color: #34495E;
                color: #ECF0F1;
                selection-background-color: #3498DB;
            }
            QPushButton {
                color: white;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QCheckBox {
                color: #ECF0F1;
            }
            QMenuBar {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QMenuBar::item {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QMenuBar::item:selected {
                background-color: #3498DB;
            }
            QMenu {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #2C3E50;
            }
            QMenu::item:selected {
                background-color: #3498DB;
            }
        """)
        self.setMinimumSize(800, 650)
        self.setGeometry(100, 100, 800, 650)
        
        # Initialize with medium difficulty
        self.change_difficulty(1)
    
    def init_menu(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_game_action = QAction('New Game', self)
        new_game_action.setShortcut('Ctrl+N')
        new_game_action.triggered.connect(self.reset_game)
        file_menu.addAction(new_game_action)
        
        save_game_action = QAction('Save Game', self)
        save_game_action.setShortcut('Ctrl+S')
        save_game_action.triggered.connect(self.save_game)
        file_menu.addAction(save_game_action)
        
        load_game_action = QAction('Load Game', self)
        load_game_action.setShortcut('Ctrl+O')
        load_game_action.triggered.connect(self.load_game)
        file_menu.addAction(load_game_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo Move', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_move)
        edit_menu.addAction(undo_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def init_timer(self):
        """Initialize the game timer"""
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_timer)
        self.game_time_seconds = 0
    
    def setup_icon(self):
        """Set up the application icon"""
        # Get project root directory and possible resource directories
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check multiple possible resource directories
        possible_resource_dirs = [
            os.path.join(project_root, 'resources'),
            os.path.join(project_root, 'src', 'resources'),
            os.path.join(project_root, '..', 'resources')
        ]
        
        # Try to find the icon in any of the resource directories
        icon_path = None
        for resource_dir in possible_resource_dirs:
            path = os.path.join(resource_dir, 'gomoku_icon.png')
            if os.path.exists(path):
                icon_path = path
                break
        
        # If icon not found, generate it
        if not icon_path:
            # Use the first directory for creating the icon
            resources_dir = possible_resource_dirs[0]
            if not os.path.exists(resources_dir):
                os.makedirs(resources_dir)
            
            icon_path = os.path.join(resources_dir, 'gomoku_icon.png')
            
            try:
                # Import the create_icon module
                import sys
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                import create_icon
                
                # Create the icon
                create_icon.create_gomoku_icon(512, icon_path)
                print(f"Generated icon at: {icon_path}")
            except ImportError as e:
                print(f"Error importing create_icon module: {e}")
                pass
        
        # Set the icon if found or created
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            print(f"Using icon from: {icon_path}")
        else:
            print("Warning: No icon found or generated")
        
    def update_timer(self):
        """Update the game timer display"""
        self.game_time_seconds += 1
        minutes = self.game_time_seconds // 60
        seconds = self.game_time_seconds % 60
        self.timer_label.setText(f"Time: {minutes:02d}:{seconds:02d}")
    
    def on_move_made(self):
        """Handle when a move is made in the game"""
        # Start timer if it's not running
        if not self.game_timer.isActive() and self.board.game_in_progress:
            self.game_timer.start(1000)  # Update every second
        
        # Enable/disable undo button based on whether undo is possible
        self.undo_btn.setEnabled(self.board.engine.can_undo())
        
        # If game is over, stop the timer
        if not self.board.game_in_progress:
            self.game_timer.stop()
    
    def reset_game(self):
        """Start a new game"""
        self.board.reset_game()
        self.game_time_seconds = 0
        self.update_timer()
        self.undo_btn.setEnabled(False)
    
    def update_status(self, message):
        """Update the status message"""
        self.status_label.setText(message)
    
    def update_statistics(self, games, player_wins, ai_wins, draws):
        """Update the game statistics display"""
        self.games_played_label.setText(f"Games Played: {games}")
        self.player_wins_label.setText(f"Your Wins: {player_wins}")
        self.ai_wins_label.setText(f"AI Wins: {ai_wins}")
        self.draws_label.setText(f"Draws: {draws}")
        
        # Calculate win rate
        if games > 0:
            win_rate = (player_wins / games) * 100
            self.win_rate_label.setText(f"Win Rate: {win_rate:.1f}%")
        else:
            self.win_rate_label.setText("Win Rate: 0%")
        
        # Save statistics to settings
        self.save_settings()
    
    def change_difficulty(self, index):
        """Change the AI difficulty level"""
        difficulty_levels = [GomokuEngine.EASY, GomokuEngine.MEDIUM, GomokuEngine.HARD]
        difficulty = difficulty_levels[index]
        self.board.set_difficulty(difficulty)
        
        # Save settings
        self.save_settings()
    
    def undo_move(self):
        """Undo the last move"""
        if self.board.undo_last_move():
            self.undo_btn.setEnabled(self.board.engine.can_undo())
            self.update_status("Move undone. Your turn (Black)")
    
    # Sound effects feature has been removed
    def toggle_sound(self, enabled):
        """This method is kept for backward compatibility but does nothing now that sound effects are removed"""
        # Save settings
        self.save_settings()
    
    def save_game(self):
        """Save the current game to a file"""
        if not self.board.game_in_progress:
            QMessageBox.information(self, "Save Game", "No game in progress to save.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Game", "", "Gomoku Save Files (*.gomoku)")
        if not file_path:
            return
            
        # If no extension was provided, add .gomoku
        if not file_path.endswith('.gomoku'):
            file_path += '.gomoku'
            
        # Get the current board state
        board_state = self.board.get_board_state()
        
        # Create a dictionary with game data
        game_data = {
            "board": board_state,
            "player_turn": self.board.player_turn,
            "time": self.game_time_seconds,
            "difficulty": self.difficulty_selector.currentIndex()
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(game_data, f)
            QMessageBox.information(self, "Save Game", "Game saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the game: {str(e)}")
    
    def load_game(self):
        """Load a game from a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Game", "", "Gomoku Save Files (*.gomoku)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                game_data = json.load(f)
                
            # Reset the game first
            self.board.reset_game()
            
            # Set difficulty
            if "difficulty" in game_data:
                self.difficulty_selector.setCurrentIndex(game_data["difficulty"])
            
            # Load the board state
            if "board" in game_data:
                board = game_data["board"]
                
                # Apply moves to the board
                player_stones = 0
                ai_stones = 0
                
                for row in range(len(board)):
                    for col in range(len(board[row])):
                        if board[row][col] == GomokuEngine.PLAYER:
                            self.board.engine.make_move(row, col, GomokuEngine.PLAYER)
                            self.board.cells[row][col].set_value(GomokuEngine.PLAYER)
                            player_stones += 1
                        elif board[row][col] == GomokuEngine.AI:
                            self.board.engine.make_move(row, col, GomokuEngine.AI)
                            self.board.cells[row][col].set_value(GomokuEngine.AI)
                            ai_stones += 1
            
            # Set player turn
            if "player_turn" in game_data:
                self.board.player_turn = game_data["player_turn"]
            else:
                # If not specified, determine by number of stones
                self.board.player_turn = (player_stones == ai_stones)
            
            # Set game time
            if "time" in game_data:
                self.game_time_seconds = game_data["time"]
                self.update_timer()
            
            # Start timer if the game is in progress
            self.board.game_in_progress = True
            self.game_timer.start(1000)
            
            # Update status
            if self.board.player_turn:
                self.update_status("Your turn (Black)")
            else:
                self.update_status("AI's turn (White)")
                
            # Enable undo if possible
            self.undo_btn.setEnabled(self.board.engine.can_undo())
            
            QMessageBox.information(self, "Load Game", "Game loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load the game: {str(e)}")
    
    def save_settings(self):
        """Save user preferences"""
        settings = {
            "difficulty": self.difficulty_selector.currentIndex(),
            "statistics": {
                "games_played": self.board.games_played,
                "player_wins": self.board.player_wins,
                "ai_wins": self.board.ai_wins,
                "draws": self.board.draws
            }
        }
        
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check multiple possible resource directories
        possible_resource_dirs = [
            os.path.join(project_root, 'resources'),
            os.path.join(project_root, 'src', 'resources'),
            os.path.join(project_root, '..', 'resources')
        ]
        
        # Use the first resource directory that exists, or create one
        settings_dir = next((d for d in possible_resource_dirs if os.path.exists(d)), possible_resource_dirs[0])
        
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
            print(f"Created settings directory: {settings_dir}")
            
        settings_path = os.path.join(settings_dir, 'settings.json')
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
            print(f"Settings saved to: {settings_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load user preferences"""
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check multiple possible resource directories
        possible_resource_dirs = [
            os.path.join(project_root, 'resources'),
            os.path.join(project_root, 'src', 'resources'),
            os.path.join(project_root, '..', 'resources')
        ]
        
        # Try to find settings file in any of the resource directories
        settings_path = None
        for resource_dir in possible_resource_dirs:
            path = os.path.join(resource_dir, 'settings.json')
            if os.path.exists(path):
                settings_path = path
                break
        
        if settings_path:
            try:
                print(f"Loading settings from: {settings_path}")
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                if "difficulty" in settings:
                    self.difficulty_selector.setCurrentIndex(settings["difficulty"])
                
                if "statistics" in settings:
                    stats = settings["statistics"]
                    self.board.games_played = stats.get("games_played", 0)
                    self.board.player_wins = stats.get("player_wins", 0)
                    self.board.ai_wins = stats.get("ai_wins", 0)
                    self.board.draws = stats.get("draws", 0)
                    self.update_statistics(
                        self.board.games_played, 
                        self.board.player_wins,
                        self.board.ai_wins, 
                        self.board.draws
                    )
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            print("No settings file found, using defaults")
    
    def show_about_dialog(self):
        """Show the About dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def show_about(self):
        """Show the About dialog (alias for show_about_dialog)"""
        self.show_about_dialog()


class AboutDialog(QDialog):
    """About dialog showing information about the game"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Five in a Row")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Add game title
        title = QLabel("Five in a Row (Gomoku)")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        info = QTextBrowser()
        info.setOpenExternalLinks(True)
        info.setHtml("""
        <p style='text-align: center;'><b>Version 1.1</b></p>
        <p>Five in a Row (also known as Gomoku or Gobang) is a classic two-player strategy game played on a 15×15 grid. 
        Players take turns placing stones (black and white) on the board, and the first to get exactly 
        five stones in a row (horizontally, vertically, or diagonally) wins.</p>
        
        <p><b>Features:</b></p>
        <ul>
            <li>Play against AI with adjustable difficulty</li>
            <li>Undo moves</li>
            <li>Game statistics</li>
            <li>Save and load games</li>
            <!-- Sound effects removed -->
            <li>Game timer</li>
        </ul>
        
        <p><b>Technology:</b></p>
        <ul>
            <li>Frontend: Python with PyQt5</li>
            <li>Backend: C++ with Alpha-Beta Pruning AI algorithm</li>
        </ul>
        
        <p style='text-align: center;'>&copy; 2025</p>
        """)
        layout.addWidget(info)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = GomokuWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
