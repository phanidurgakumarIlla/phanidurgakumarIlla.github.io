import turtle
import random
import time 

# @python.coder_
WIDTH = 500
HEIGHT = 500
FOOD_SIZE = 10
DELAY = 100  # Milliseconds for game loop speed
STEP = 20    # Snake movement step (must be an integer)

offsets = {
    "up": (0, STEP),
    "down": (0, -STEP),
    "left": (-STEP, 0),
    "right": (STEP, 0)
}

# Global variables
snake = []
snake_direction = "up"
food_pos = [0, 0] 
pen = None
food = None
screen = None
score_pen = None
border_pen = None # New: Pen for drawing the border
score = 0
game_is_running = False 

def update_score(final_message=False):
    """Clears and rewrites the current score or final message on the screen."""
    score_pen.clear()
    
    if final_message:
        score_pen.goto(0, 50)
        score_pen.color("red")
        score_pen.write(f"GAME OVER!", align="center", font=("Courier", 30, "bold"))
        score_pen.goto(0, 0)
        score_pen.color("white")
        score_pen.write(f"Final Score: {score}", align="center", font=("Courier", 24, "normal"))
        score_pen.goto(0, -50)
        score_pen.write("Press 'R' to Replay or 'Q' to Quit.", align="center", font=("Courier", 16, "normal"))
    else:
        score_pen.goto(0, HEIGHT // 2 - 40)
        score_pen.color("white")
        score_pen.write(f"Score: {score}", align="center", font=("Courier", 18, "normal"))

# --- Game Control Functions ---

def end_game_options():
    """Sets up listeners for the replay and quit keys."""
    # Disable direction keys during game over
    screen.onkey(None, "Up")
    screen.onkey(None, "Right")
    screen.onkey(None, "Down")
    screen.onkey(None, "Left")
    
    # Set up end-game options
    screen.onkey(replay, "r")
    screen.onkey(replay, "R")
    screen.onkey(quit_game, "q")
    screen.onkey(quit_game, "Q")

def replay():
    """Starts a new game."""
    # Disable replay/quit keys
    screen.onkey(None, "r")
    screen.onkey(None, "q")
    
    # Re-enable direction keys
    screen.onkey(go_up, "Up")
    screen.onkey(go_right, "Right")
    screen.onkey(go_down, "Down")
    screen.onkey(go_left, "Left")
    
    reset() # Start a fresh game

def quit_game():
    """Closes the turtle window."""
    global game_is_running
    game_is_running = False
    turtle.bye() # Cleanly close the turtle window

# --- Game Logic Functions ---

def reset():
    """Initializes or resets the game state."""
    global snake, snake_direction, food_pos, score, game_is_running

    # Stop any previous game loop
    if screen:
        screen.ontimer(None, DELAY) 
    
    # If the game was just running, show game over screen and prompt for input
    if game_is_running:
        update_score(final_message=True) # Show final score and options
        end_game_options()
        game_is_running = False
        return # Stop reset, wait for user input
    
    # --- Start of a new game ---
    game_is_running = True
    
    # Reset game state
    snake = [[0, -2 * STEP], [0, -STEP], [0, 0]]
    snake_direction = "up"
    score = 0 # Reset score
    
    # Reset score display position (top center)
    update_score()
    
    # Place food randomly
    food_pos = get_random_food_pos()
    
    # Clear snake stamps from previous game
    pen.clearstamps()
    if food:
        food.goto(food_pos[0], food_pos[1])
    
    # Start the game loop
    move_snake()


def move_snake():
    """
    Handles the main game logic: moving the snake, checking for collisions,
    border collision, and redrawing the snake.
    """
    global snake_direction

    if not game_is_running:
        return

    # 1. Calculate the next position for the head
    new_head = snake[-1].copy()
    new_head[0] += offsets[snake_direction][0]
    new_head[1] += offsets[snake_direction][1]
    
    # 2. Check Self-Collision
    if new_head in snake:
        return reset()

    # --- Border Collision Check ---
    x, y = new_head[0], new_head[1]
    
    # The collision boundary is exactly at the edge of the border drawing.
    # So, (WIDTH/2) and (HEIGHT/2) are the exact limits.
    # The snake is STEP (20) wide, so it's centered at these coordinates.
    # If the head's center is at WIDTH/2, half of it is outside.
    # So, the effective boundary is (WIDTH/2 - STEP/2)
    # The current coordinate system runs from -WIDTH/2 to WIDTH/2.
    # If snake is 20 wide, its rightmost pixel is at x+10, leftmost at x-10.
    # So, if x+10 >= WIDTH/2 or x-10 <= -WIDTH/2, it's a collision.
    # This simplifies to checking if the center x is >= (WIDTH/2 - STEP/2) or <= (-WIDTH/2 + STEP/2)
    
    # Using HALF_LIMIT as where the center of the snake head hits the border line.
    HALF_LIMIT_X = (WIDTH // 2) - (STEP // 2)
    HALF_LIMIT_Y = (HEIGHT // 2) - (STEP // 2)

    if (x >= HALF_LIMIT_X) or \
       (x <= -HALF_LIMIT_X) or \
       (y >= HALF_LIMIT_Y) or \
       (y <= -HALF_LIMIT_Y):
        return reset()
    # -------------------------------------------
    
    # 3. Update Snake Body
    snake.append(new_head)

    # Check food collision and adjust length
    if food_collision():
        pass 
    else:
        snake.pop(0) # Keep the snake the same length

    # 4. Drawing Logic
    pen.clearstamps()

    for segment in snake:
        pen.goto(segment[0], segment[1])
        pen.stamp()

    screen.update()

    # 5. Schedule the next move
    turtle.ontimer(move_snake, DELAY)


def food_collision():
    """Checks if the snake's head has collided with the food and updates score."""
    global food_pos, score
    
    if get_distance(snake[-1], food_pos) < STEP: 
        score += 10 
        update_score() 

        food_pos = get_random_food_pos()
        food.goto(food_pos[0], food_pos[1])
        return True
    return False


def get_random_food_pos():
    """Returns a random [x, y] coordinate for the food on the grid."""
    # Ensure food spawns within the visible play area, inside the border.
    # The maximum coordinate for food should be (HALF_WIDTH - STEP)
    max_coord = (WIDTH // 2) - STEP 
    
    # random.randrange ensures food is on the grid and within bounds
    x = random.randrange(-max_coord, max_coord + STEP, STEP)
    y = random.randrange(-max_coord, max_coord + STEP, STEP)
    
    return [x, y]


def get_distance(pos1, pos2):
    """Calculates the Euclidean distance between two points."""
    x1, y1 = pos1
    x2, y2 = pos2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


# --- Direction Control Functions ---
def go_up():
    global snake_direction
    if snake_direction != "down": snake_direction = "up"
def go_right():
    global snake_direction
    if snake_direction != "left": snake_direction = "right"
def go_down():
    global snake_direction
    if snake_direction != "up": snake_direction = "down"
def go_left():
    global snake_direction
    if snake_direction != "right": snake_direction = "left"

# --- Drawing Border Function ---
def draw_border():
    """Draws a red border around the game area."""
    border_pen.penup()
    border_pen.goto(-WIDTH // 2, HEIGHT // 2) # Top-left corner
    border_pen.pendown()
    border_pen.pencolor("red")
    border_pen.pensize(5) # Thicker border
    
    # Draw a rectangle
    for _ in range(2):
        border_pen.forward(WIDTH)
        border_pen.right(90)
        border_pen.forward(HEIGHT)
        border_pen.right(90)
    border_pen.penup() # Lift the pen when done

# --- Setup and Initialization ---

# Screen Setup
screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("Snake Game")
screen.bgcolor("black")
screen.tracer(0) 

# Pen (Snake) Setup
pen = turtle.Turtle("square")
pen.penup()
pen.pencolor("yellow")
pen.speed(0)
pen.hideturtle()

# Food Setup
food = turtle.Turtle()
food.shape("circle")
food.color("red")
food.shapesize(FOOD_SIZE / STEP) 
food.penup()
food.speed(0)

# Score Pen Setup
score_pen = turtle.Turtle()
score_pen.speed(0)
score_pen.color("white")
score_pen.penup()
score_pen.hideturtle()

# Border Pen Setup (NEW)
border_pen = turtle.Turtle()
border_pen.speed(0)
border_pen.hideturtle()
border_pen.penup() # Ensure pen is up initially

# Draw the border once
draw_border()

# Event Handlers (Direction Keys)
screen.listen()
screen.onkey(go_up, "Up")
screen.onkey(go_right, "Right")
screen.onkey(go_down, "Down")
screen.onkey(go_left, "Left")

# Start the game
reset()

# Keep the turtle window open
turtle.done()
