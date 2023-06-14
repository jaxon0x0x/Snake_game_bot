import pygame
import random
from enum import Enum
from collections import namedtuple, deque
import matplotlib.pyplot as plt

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 220


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.score_history = []  # Store the score at each step
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, direction=None):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Use AI-generated direction if provided, otherwise use user input
        if direction is not None:
            self.direction = direction
        else:
            self._handle_user_input()

        # 2. move
        self._move(self.direction)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Store the score at each step
        self.score_history.append(self.score)

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score

    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _handle_user_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction = Direction.LEFT
        elif keys[pygame.K_RIGHT]:
            self.direction = Direction.RIGHT
        elif keys[pygame.K_UP]:
            self.direction = Direction.UP
        elif keys[pygame.K_DOWN]:
            self.direction = Direction.DOWN

    def get_game_state(self):
        game_state = []
        for x in range(self.w // BLOCK_SIZE):
            row = []
            for y in range(self.h // BLOCK_SIZE):
                if Point(x * BLOCK_SIZE, y * BLOCK_SIZE) in self.snake:
                    row.append(1)
                elif self.food == Point(x * BLOCK_SIZE, y * BLOCK_SIZE):
                    row.append(2)
                else:
                    row.append(0)
            game_state.append(row)
        return game_state


def bfs(game):
    start = game.head
    goal = game.food

    queue = deque([(start, [])])
    visited = set([start])

    while queue:
        current, path = queue.popleft()
        if current == goal:
            if len(path) > 0:
                return path[0]
            else:
                return game.direction

        for direction in Direction:
            next_pos = get_next_position(current, direction)
            if is_valid_move(next_pos, game):
                if next_pos not in visited:
                    queue.append((next_pos, path + [direction]))
                    visited.add(next_pos)

    return game.direction


def get_next_position(current, direction):
    x, y = current
    if direction == Direction.RIGHT:
        return Point(x + BLOCK_SIZE, y)
    elif direction == Direction.LEFT:
        return Point(x - BLOCK_SIZE, y)
    elif direction == Direction.DOWN:
        return Point(x, y + BLOCK_SIZE)
    elif direction == Direction.UP:
        return Point(x, y - BLOCK_SIZE)


def is_valid_move(position, game):
    x, y = position
    if x < 0 or x >= game.w or y < 0 or y >= game.h:
        return False
    if position in game.snake[1:]:
        return False
    return True


if __name__ == '__main__':
    score_history = []
    step_history = []
    game_history=[]
    for _ in range(10):
        game = SnakeGame()
        steps = 0

        while True:
            # Use BFS to get the direction for the bot
            bot_direction = bfs(game)
            game_over, score = game.play_step(direction=bot_direction)

            if game_over:


                steps += 1

                break

        game_history.append(_ + 1)
        score_history.append(score)


        print('Game:', len(score_history), 'Score:', score)

    # Plot the score history
    plt.plot(game_history, score_history)

    pygame.display.set_caption('Score Progression')
    plt.xlabel('Number of games')
    plt.ylabel('Score')
    plt.title('Score Progression')
    plt.show()

    pygame.quit()

    pygame.quit()