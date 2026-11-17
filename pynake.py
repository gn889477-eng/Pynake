"""Pynake - Snake clone for pygame.

Install:  pip install pygame
Run:      python pynake.py

Controls:
  Arrow keys / WASD  - move
  P                  - pause
  R / Enter / Space  - restart after game over
  Esc                - quit
"""
import random
import sys

import pygame

CELL = 25
COLS = 30
ROWS = 30
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
FPS = 12

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (150, 150, 150)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

KEYMAP = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}


class Pynake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # head first
        self.direction = RIGHT
        self.queue = []  # buffered turns so quick key presses aren't lost
        self.score = 0
        self.alive = True
        self.food = self.spawn_food()

    def spawn_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in self.body]
        return random.choice(free) if free else None

    def turn(self, new_dir):
        last = self.queue[-1] if self.queue else self.direction
        # ignore reversing and repeats
        if new_dir == last or (new_dir[0] == -last[0] and new_dir[1] == -last[1]):
            return
        if len(self.queue) < 3:
            self.queue.append(new_dir)

    def step(self):
        if not self.alive:
            return
        if self.queue:
            self.direction = self.queue.pop(0)
        hx, hy = self.body[0]
        head = (hx + self.direction[0], hy + self.direction[1])

        growing = head == self.food
        # the tail moves away this tick unless we're growing
        check_body = self.body if growing else self.body[:-1]
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in check_body:
            self.alive = False
            return

        self.body.insert(0, head)
        if growing:
            self.score += 1
            self.food = self.spawn_food()
            if self.food is None:  # board full = win
                self.alive = False
        else:
            self.body.pop()

    def draw(self, screen, font):
        screen.fill(BLACK)
        for x, y in self.body:
            pygame.draw.rect(screen, WHITE, (x * CELL, y * CELL, CELL, CELL))
        if self.food:
            fx, fy = self.food
            pygame.draw.rect(screen, RED, (fx * CELL, fy * CELL, CELL, CELL))
        screen.blit(font.render(f"Score: {self.score}", True, WHITE), (12, 8))


def centered(screen, font, text, y, color=WHITE):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pynake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)
    big = pygame.font.SysFont("consolas", 52, bold=True)

    game = Pynake()
    best = 0
    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if game.alive:
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif event.key in KEYMAP and not paused:
                        game.turn(KEYMAP[event.key])
                elif event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    game.reset()
                    paused = False

        if not paused:
            game.step()
        best = max(best, game.score)

        game.draw(screen, font)
        if paused:
            centered(screen, big, "PAUSED", HEIGHT // 2 - 30)
        if not game.alive:
            centered(screen, big, "GAME OVER", HEIGHT // 2 - 70)
            centered(screen, font, f"Score: {game.score}   Best: {best}", HEIGHT // 2 + 5)
            centered(screen, font, "Press R to restart", HEIGHT // 2 + 45, GRAY)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
