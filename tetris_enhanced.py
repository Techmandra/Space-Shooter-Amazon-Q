import pygame
import random
import time
import sys
import os
import math

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

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Function to create block textures if they don't exist
def create_block_texture(filename, color):
    if not os.path.exists(filename):
        # Create a textured block
        block_surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        
        # Fill with base color
        block_surface.fill(color)
        
        # Add highlights and shadows for 3D effect
        lighter = tuple(min(c + 50, 255) for c in color)
        darker = tuple(max(c - 50, 0) for c in color)
        
        # Top highlight
        pygame.draw.line(block_surface, lighter, (0, 0), (GRID_SIZE-1, 0), 2)
        pygame.draw.line(block_surface, lighter, (0, 0), (0, GRID_SIZE-1), 2)
        
        # Bottom shadow
        pygame.draw.line(block_surface, darker, (1, GRID_SIZE-1), (GRID_SIZE-1, GRID_SIZE-1), 2)
        pygame.draw.line(block_surface, darker, (GRID_SIZE-1, 1), (GRID_SIZE-1, GRID_SIZE-1), 2)
        
        # Inner details
        pygame.draw.rect(block_surface, darker, (5, 5, GRID_SIZE-10, GRID_SIZE-10), 1)
        
        # Save the image
        pygame.image.save(block_surface, filename)
    
    return pygame.image.load(filename)

# Create and load block textures
block_textures = []
for i, color in enumerate(COLORS):
    texture = create_block_texture(f'images/block_{i}.png', color)
    block_textures.append(texture)

# Load or create background image
def create_background():
    filename = 'images/tetris_bg.png'
    if not os.path.exists(filename):
        # Create a simple gradient background
        bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for y in range(SCREEN_HEIGHT):
            # Create a dark blue to black gradient
            color_value = max(0, 50 - y // 10)
            bg_surface.fill((0, 0, color_value), (0, y, SCREEN_WIDTH, 1))
            
        # Add some "stars"
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            pygame.draw.circle(bg_surface, (brightness, brightness, brightness), (x, y), size)
            
        pygame.image.save(bg_surface, filename)
    
    return pygame.image.load(filename)

background_image = create_background()

# Sound effects
try:
    pygame.mixer.init()
    
    # Create placeholder sound files if they don't exist
    def create_sound_file(filename, duration, frequency):
        if not os.path.exists(filename):
            # This is just a placeholder - in a real game you'd use actual sound files
            pygame.mixer.Sound.notes(frequency, duration).save(filename)
            
    # Create or load sound effects
    if not os.path.exists('sounds'):
        os.makedirs('sounds')
        
    move_sound = pygame.mixer.Sound('sounds/move.wav') if os.path.exists('sounds/move.wav') else None
    rotate_sound = pygame.mixer.Sound('sounds/rotate.wav') if os.path.exists('sounds/rotate.wav') else None
    drop_sound = pygame.mixer.Sound('sounds/drop.wav') if os.path.exists('sounds/drop.wav') else None
    clear_sound = pygame.mixer.Sound('sounds/clear.wav') if os.path.exists('sounds/clear.wav') else None
    game_over_sound = pygame.mixer.Sound('sounds/game_over.wav') if os.path.exists('sounds/game_over.wav') else None
    
except:
    # If sound initialization fails, continue without sound
    move_sound = None
    rotate_sound = None
    drop_sound = None
    clear_sound = None
    game_over_sound = None

class AnimationEffect:
    def __init__(self, x, y, effect_type, duration=0.5):
        self.x = x
        self.y = y
        self.effect_type = effect_type  # 'clear', 'lock', etc.
        self.start_time = time.time()
        self.duration = duration
        self.active = True
    
    def update(self):
        if time.time() - self.start_time > self.duration:
            self.active = False
    
    def draw(self):
        if not self.active:
            return
            
        progress = (time.time() - self.start_time) / self.duration
        
        if self.effect_type == 'clear':
            # Line clear flash effect
            alpha = int(255 * (1 - progress))
            flash_surface = pygame.Surface((PLAY_AREA_WIDTH, GRID_SIZE), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, alpha))
            screen.blit(flash_surface, (PLAY_AREA_X, PLAY_AREA_Y + self.y * GRID_SIZE))
        
        elif self.effect_type == 'lock':
            # Block lock effect - small sparkles
            for _ in range(3):
                sparkle_x = PLAY_AREA_X + self.x * GRID_SIZE + random.randint(0, GRID_SIZE)
                sparkle_y = PLAY_AREA_Y + self.y * GRID_SIZE + random.randint(0, GRID_SIZE)
                size = int(5 * (1 - progress))
                pygame.draw.circle(screen, WHITE, (sparkle_x, sparkle_y), size)

class Tetromino:
    def __init__(self, x, y):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.texture = block_textures[self.shape_index]
        self.x = x
        self.y = y
        self.rotation = 0
        self.drop_animation = 0  # For smooth dropping animation
    
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
            return False
        else:
            self.rotation = (self.rotation + 1) % 4
            if rotate_sound:
                rotate_sound.play()
            return True
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if not self.is_valid_position(board):
            self.x -= dx
            self.y -= dy
            return False
        
        if dx != 0 and move_sound:
            move_sound.play()
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
    
    def lock(self, board, animations):
        shape_height = len(self.shape)
        shape_width = len(self.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.shape[r][c] == 0:
                    continue
                
                board_y = self.y + r
                board_x = self.x + c
                
                if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                    board[board_y][board_x] = self.shape_index + 1  # Store shape index + 1 (0 means empty)
                    # Add lock animation
                    animations.append(AnimationEffect(board_x, board_y, 'lock', 0.3))
        
        if drop_sound:
            drop_sound.play()
    
    def draw(self, ghost=False):
        shape_height = len(self.shape)
        shape_width = len(self.shape[0])
        
        for r in range(shape_height):
            for c in range(shape_width):
                if self.shape[r][c] == 0:
                    continue
                
                # Calculate the position on screen
                x = PLAY_AREA_X + (self.x + c) * GRID_SIZE
                y = PLAY_AREA_Y + (self.y + r) * GRID_SIZE
                
                if ghost:
                    # Draw ghost piece (semi-transparent)
                    ghost_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                    ghost_surface.fill((255, 255, 255, 50))
                    screen.blit(ghost_surface, (x, y))
                    pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)
                else:
                    # Draw actual piece with texture
                    screen.blit(self.texture, (x, y))

class Game:
    def __init__(self):
        self.state = START_MENU
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.ghost_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1.0  # seconds per drop
        self.last_fall_time = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.animations = []
        self.lines_to_clear = []
        self.clear_animation_time = 0
    
    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.update_ghost_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1.0
        self.last_fall_time = time.time()
        self.animations = []
        self.lines_to_clear = []
        self.clear_animation_time = 0
    
    def update_ghost_piece(self):
        # Create a ghost piece that shows where the current piece will land
        if not self.current_piece:
            return
            
        self.ghost_piece = Tetromino(self.current_piece.x, self.current_piece.y)
        self.ghost_piece.shape = self.current_piece.shape
        self.ghost_piece.shape_index = self.current_piece.shape_index
        
        # Move the ghost piece down until it hits something
        while self.ghost_piece.move(0, 1):
            pass
    
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
                        if self.current_piece.move(-1, 0):
                            self.update_ghost_piece()
                    elif event.key == pygame.K_RIGHT:
                        if self.current_piece.move(1, 0):
                            self.update_ghost_piece()
                    elif event.key == pygame.K_DOWN:
                        self.current_piece.move(0, 1)
                    elif event.key == pygame.K_UP:
                        if self.current_piece.rotate():
                            self.update_ghost_piece()
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
        
        # Update animations
        for anim in self.animations[:]:
            anim.update()
            if not anim.active:
                self.animations.remove(anim)
        
        # Handle line clearing animation
        if self.lines_to_clear:
            current_time = time.time()
            if current_time - self.clear_animation_time > 0.5:  # Animation duration
                # Remove the lines and shift blocks down
                for y in sorted(self.lines_to_clear):
                    for y2 in range(y, 0, -1):
                        for x in range(GRID_WIDTH):
                            self.board[y2][x] = self.board[y2-1][x]
                    # Clear the top line
                    for x in range(GRID_WIDTH):
                        self.board[0][x] = 0
                
                # Update score
                self.update_score(len(self.lines_to_clear))
                
                # Play sound
                if clear_sound:
                    clear_sound.play()
                
                # Reset
                self.lines_to_clear = []
            return
        
        # Check if it's time for the piece to fall
        current_time = time.time()
        if current_time - self.last_fall_time > self.fall_speed:
            if not self.current_piece.move(0, 1):
                self.lock_piece()
            self.last_fall_time = current_time
    
    def lock_piece(self):
        # Lock the current piece in place
        self.current_piece.lock(self.board, self.animations)
        
        # Check for completed lines
        self.check_lines()
        
        if not self.lines_to_clear:
            # Create a new piece if no lines to clear
            self.current_piece = self.next_piece
            self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
            self.update_ghost_piece()
            
            # Check for game over
            if not self.current_piece.is_valid_position(self.board):
                self.state = GAME_OVER
                if game_over_sound:
                    game_over_sound.play()
    
    def check_lines(self):
        self.lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y][x] != 0 for x in range(GRID_WIDTH)):
                self.lines_to_clear.append(y)
                # Add clear animation
                self.animations.append(AnimationEffect(0, y, 'clear', 0.5))
        
        if self.lines_to_clear:
            self.clear_animation_time = time.time()
    
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
        
        # Draw the grid and blocks
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell_x = PLAY_AREA_X + x * GRID_SIZE
                cell_y = PLAY_AREA_Y + y * GRID_SIZE
                
                if self.board[y][x] != 0:
                    # Draw block with texture
                    block_index = self.board[y][x] - 1  # Convert back to 0-based index
                    screen.blit(block_textures[block_index], (cell_x, cell_y))
                else:
                    # Draw empty cell
                    pygame.draw.rect(screen, GRAY, (cell_x, cell_y, GRID_SIZE, GRID_SIZE), 1)
        
        # Draw animations
        for anim in self.animations:
            anim.draw()
        
        # Highlight lines being cleared
        for y in self.lines_to_clear:
            flash_progress = (time.time() - self.clear_animation_time) / 0.5  # 0.5s animation
            if int(flash_progress * 10) % 2 == 0:  # Flash effect
                pygame.draw.rect(screen, WHITE, 
                               (PLAY_AREA_X, PLAY_AREA_Y + y * GRID_SIZE, 
                                PLAY_AREA_WIDTH, GRID_SIZE))
    
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
                
                screen.blit(self.next_piece.texture, (x, y))
        
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
        # Draw animated background
        screen.blit(background_image, (0, 0))
        
        # Draw animated title
        title_y_offset = math.sin(time.time() * 2) * 10
        title = self.font.render("TETRIS", True, WHITE)
        instructions = self.font.render("Press ENTER to start", True, YELLOW)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 
                          SCREEN_HEIGHT // 2 - 50 + title_y_offset))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 
                                SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER to return to menu", True, YELLOW)
        
        # Pulsating effect
        scale = 1.0 + 0.1 * math.sin(time.time() * 4)
        game_over_width = int(game_over_text.get_width() * scale)
        game_over_height = int(game_over_text.get_height() * scale)
        scaled_text = pygame.transform.scale(game_over_text, (game_over_width, game_over_height))
        
        screen.blit(scaled_text, (SCREEN_WIDTH // 2 - game_over_width // 2, SCREEN_HEIGHT // 2 - 50))
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
        # Draw background
        screen.blit(background_image, (0, 0))
        
        if self.state == START_MENU:
            self.draw_start_menu()
        elif self.state == GAME_ACTIVE or self.state == GAME_PAUSED:
            self.draw_board()
            
            # Draw ghost piece
            if self.ghost_piece:
                self.ghost_piece.draw(ghost=True)
                
            # Draw current piece
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
