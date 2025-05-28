import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Calculate the actual play area size and position
PLAY_AREA_WIDTH = GRID_WIDTH * GRID_SIZE
PLAY_AREA_HEIGHT = GRID_HEIGHT * GRID_SIZE
PLAY_AREA_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - PLAY_AREA_WIDTH) // 2
PLAY_AREA_Y = (SCREEN_HEIGHT - PLAY_AREA_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino shapes and colors
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

# Game states
START_MENU = 0
GAME_ACTIVE = 1
GAME_OVER = 2
GAME_PAUSED = 3

class Tetromino:
    def __init__(self, x, y):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.x = x
        self.y = y
        self.rotation = 0
    
    def rotate(self):
        # Create a new rotated shape
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        # Check if rotation is valid
        old_shape = self.shape
        self.shape = rotated
        if not self.is_valid_position(board):
            self.shape = old_shape
        else:
            self.rotation = (self.rotation + 1) % 4
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if not self.is_valid_position(board):
            self.x -= dx
            self.y -= dy
            return False
        return True
    
    def is_valid_position(self, board):
        shape_height = len(self.shape)
        shape_width = len(self.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.shape[r][c] == 0:
                    continue
                
                # Check if out of bounds
                board_x = self.x + c
                board_y = self.y + r
                
                if (board_x < 0 or board_x >= GRID_WIDTH or 
                    board_y < 0 or board_y >= GRID_HEIGHT):
                    return False
                
                # Check if collides with placed blocks
                if board_y >= 0 and board[board_y][board_x] != 0:
                    return False
        
        return True
    
    def lock(self, board):
        shape_height = len(self.shape)
        shape_width = len(self.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.shape[r][c] == 0:
                    continue
                
                board_y = self.y + r
                board_x = self.x + c
                
                if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                    board[board_y][board_x] = self.color
    
    def draw(self):
        shape_height = len(self.shape)
        shape_width = len(self.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.shape[r][c] == 0:
                    continue
                
                # Calculate the position on screen
                x = PLAY_AREA_X + (self.x + c) * GRID_SIZE
                y = PLAY_AREA_Y + (self.y + r) * GRID_SIZE
                
                pygame.draw.rect(screen, self.color, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)

class Game:
    def __init__(self):
        self.state = START_MENU
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1.0  # seconds per drop
        self.last_fall_time = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
    
    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1.0
        self.last_fall_time = time.time()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == START_MENU and event.key == pygame.K_RETURN:
                    self.state = GAME_ACTIVE
                    self.reset()
                elif self.state == GAME_OVER and event.key == pygame.K_RETURN:
                    self.state = START_MENU
                elif self.state == GAME_ACTIVE:
                    if event.key == pygame.K_p:
                        self.state = GAME_PAUSED
                    elif event.key == pygame.K_LEFT:
                        self.current_piece.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.current_piece.move(0, 1)
                    elif event.key == pygame.K_UP:
                        self.current_piece.rotate()
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.current_piece.move(0, 1):
                            pass
                        self.lock_piece()
                elif self.state == GAME_PAUSED and event.key == pygame.K_p:
                    self.state = GAME_ACTIVE
    
    def update(self):
        if self.state != GAME_ACTIVE:
            return
        
        # Check if it's time for the piece to fall
        current_time = time.time()
        if current_time - self.last_fall_time > self.fall_speed:
            if not self.current_piece.move(0, 1):
                self.lock_piece()
            self.last_fall_time = current_time
    
    def lock_piece(self):
        # Lock the current piece in place
        self.current_piece.lock(self.board)
        
        # Check for completed lines
        lines_cleared = self.clear_lines()
        if lines_cleared > 0:
            self.update_score(lines_cleared)
        
        # Create a new piece
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        # Check for game over
        if not self.current_piece.is_valid_position(self.board):
            self.state = GAME_OVER
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.board[y][x] != 0 for x in range(GRID_WIDTH)):
                # Remove the line
                for y2 in range(y, 0, -1):
                    for x in range(GRID_WIDTH):
                        self.board[y2][x] = self.board[y2-1][x]
                # Clear the top line
                for x in range(GRID_WIDTH):
                    self.board[0][x] = 0
                lines_cleared += 1
        
        return lines_cleared
    
    def update_score(self, lines_cleared):
        # Update score based on lines cleared
        points_per_line = [0, 40, 100, 300, 1200]  # 0, 1, 2, 3, 4 lines
        self.score += points_per_line[lines_cleared] * self.level
        
        # Update lines cleared and level
        self.lines_cleared += lines_cleared
        self.level = self.lines_cleared // 10 + 1
        
        # Update fall speed based on level
        self.fall_speed = max(0.1, 1.0 - (self.level - 1) * 0.05)
    
    def draw_board(self):
        # Draw the board background
        pygame.draw.rect(screen, BLACK, (PLAY_AREA_X, PLAY_AREA_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT))
        pygame.draw.rect(screen, WHITE, (PLAY_AREA_X, PLAY_AREA_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), 2)
        
        # Draw the grid
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell_x = PLAY_AREA_X + x * GRID_SIZE
                cell_y = PLAY_AREA_Y + y * GRID_SIZE
                
                if self.board[y][x] != 0:
                    pygame.draw.rect(screen, self.board[y][x], (cell_x, cell_y, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, WHITE, (cell_x, cell_y, GRID_SIZE, GRID_SIZE), 1)
                else:
                    pygame.draw.rect(screen, GRAY, (cell_x, cell_y, GRID_SIZE, GRID_SIZE), 1)
    
    def draw_sidebar(self):
        sidebar_x = PLAY_AREA_X + PLAY_AREA_WIDTH + 20
        sidebar_y = PLAY_AREA_Y
        
        # Draw next piece preview
        next_text = self.font.render("Next:", True, WHITE)
        screen.blit(next_text, (sidebar_x, sidebar_y))
        
        # Draw the next piece
        next_piece_x = sidebar_x + 20
        next_piece_y = sidebar_y + 50
        
        shape_height = len(self.next_piece.shape)
        shape_width = len(self.next_piece.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.next_piece.shape[r][c] == 0:
                    continue
                
                x = next_piece_x + c * GRID_SIZE
                y = next_piece_y + r * GRID_SIZE
                
                pygame.draw.rect(screen, self.next_piece.color, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)
        
        # Draw score, level, and lines
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        screen.blit(score_text, (sidebar_x, next_piece_y + 150))
        screen.blit(level_text, (sidebar_x, next_piece_y + 200))
        screen.blit(lines_text, (sidebar_x, next_piece_y + 250))
        
        # Draw controls
        controls_y = next_piece_y + 320
        controls = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "P : Pause"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            screen.blit(control_text, (sidebar_x, controls_y + i * 25))
    
    def draw_start_menu(self):
        screen.fill(BLACK)
        
        title = self.font.render("TETRIS", True, WHITE)
        instructions = self.font.render("Press ENTER to start", True, YELLOW)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER to return to menu", True, YELLOW)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press P to resume", True, YELLOW)
        
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 25))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 25))
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.state == START_MENU:
            self.draw_start_menu()
        elif self.state == GAME_ACTIVE or self.state == GAME_PAUSED:
            self.draw_board()
            self.current_piece.draw()
            self.draw_sidebar()
            
            if self.state == GAME_PAUSED:
                self.draw_pause_menu()
        elif self.state == GAME_OVER:
            self.draw_board()
            self.draw_sidebar()
            self.draw_game_over()

# Global board for collision detection
board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Main game loop
def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
