
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 200


# Calculate distance between goal and current state
def dist(state, goal):
    dist = abs(goal[0] - state[0]) + abs(goal[1] - state[1])
    return dist


def greedy(direc, pos, goal, body):
    # initiate direction and value for every direction
    arah = ['DOWN', 'UP', 'LEFT', 'RIGHT']
    nilai = np.array([[0, 10], [0, -10], [-10, 0], [10, 0]])
    # append every state and distance goal-state in dictionary
    dict_state = {x: pos + i for x, i in zip(arah, nilai)}
    dict_arah = {x: dist(pos + i, goal) for x, i in zip(arah, nilai)}

    # check if candidate direction is in snake body
    # if yes, then delete the candidate direction
    for item in dict_state.items():
        if list(item[1]) in body:
            arah.remove(item[0])

    change = direc

    if len(arah) == 0:
        return change

    if direc not in arah:
        change = arah[0]

    # looking which state has the least value/distance to food
    for item in arah:
        if dict_arah[item] < dict_arah[change]:
            change = item
        elif dict_arah[item] == dict_arah[change]:
            # If the distances are equal, prioritize the direction that maintains the current direction
            if item == direc:
                change = item

    return change


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        direc = self.direction.name
        pos = self.head
        goal = self.food
        body = self.snake[1:]
        new_direction = Direction[greedy(direc, pos, goal, body)]

        if new_direction == Direction.RIGHT and self.direction == Direction.LEFT:
            new_direction = self.direction
        elif new_direction == Direction.LEFT and self.direction == Direction.RIGHT:
            new_direction = self.direction
        elif new_direction == Direction.UP and self.direction == Direction.DOWN:
            new_direction = self.direction
        elif new_direction == Direction.DOWN and self.direction == Direction.UP:
            new_direction = self.direction

        self.direction = new_direction

        self._move(self.direction)
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return game_over, self.score

    def _is_collision(self):
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
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


if __name__ == '__main__':
    num_games = 10  # Number of games to play
    scores = []  # List to store the scores of each game

    for i in range(num_games):
        game = SnakeGame()
        game_over = False
        score = 0

        while not game_over:
            game_over, score = game.play_step()

        scores.append(score)
        print(f"Game {i + 1}: Score = {score}")

    print('Average Score:', sum(scores) / num_games)
    plt.plot(range(1, num_games + 1), scores)
    plt.xlabel('Game')
    plt.ylabel('Score')
    plt.title('Snake Game Scores')
    plt.show()

    pygame.quit()