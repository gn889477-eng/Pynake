"""Pynake (Android version) - Snake for pygame with touch controls.

Works with pygame on Android (e.g. Pydroid 3 with the pygame package).

Controls:
  Swipe up / down / left / right  - turn the snake
  Tap the screen                  - start, restart after game over
  (Keyboard also works if one is attached: arrows / WASD, P pause)
"""
import random
import sys

import pygame

COLS = 20          # grid width; cell size is computed from the screen width
FPS = 9
SWIPE_MIN = 25     # pixels of finger movement that count as a swipe

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (150, 150, 150)
DARK = (25, 25, 25)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

KEYMAP = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}


class Pynake:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.reset()

    def reset(self):
        cx, cy = self.cols // 2, self.rows // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # head first
        self.direction = RIGHT
        self.queue = []
        self.score = 0
        self.alive = True
        self.started = False   # waits for the first swipe/tap before moving
        self.food = self.spawn_food()

    def spawn_food(self):
        free = [(x, y) for x in range(self.cols) for y in range(self.rows)
                if (x, y) not in self.body]
        return random.choice(free) if free else None

    def turn(self, new_dir):
        last = self.queue[-1] if self.queue else self.direction
        if new_dir == last or (new_dir[0] == -last[0] and new_dir[1] == -last[1]):
            return
        if len(self.queue) < 3:
            self.queue.append(new_dir)
        self.started = True

    def step(self):
        if not self.alive or not self.started:
            return
        if self.queue:
            self.direction = self.queue.pop(0)
        hx, hy = self.body[0]
        head = (hx + self.direction[0], hy + self.direction[1])

        growing = head == self.food
        check_body = self.body if growing else self.body[:-1]
        if not (0 <= head[0] < self.cols and 0 <= head[1] < self.rows) or head in check_body:
            self.alive = False
            return

        self.body.insert(0, head)
        if growing:
            self.score += 1
            self.food = self.spawn_food()
            if self.food is None:
                self.alive = False
        else:
            self.body.pop()


def centered(screen, font, text, y, color=WHITE):
    surf = font.render(text, True, color)
    screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0))  # full screen on Android
    sw, sh = screen.get_size()
    pygame.display.set_caption("Pynake")
    clock = pygame.time.Clock()

    cell = sw // COLS
    cols = COLS
    top_bar = max(cell * 2, sh // 14)          # room for the score
    rows = (sh - top_bar) // cell
    off_x = (sw - cols * cell) // 2
    off_y = top_bar + (sh - top_bar - rows * cell) // 2

    font = pygame.font.SysFont("monospace", max(18, sw // 18))
    big = pygame.font.SysFont("monospace", max(30, sw // 9), bold=True)

    game = Pynake(cols, rows)
    best = 0
    paused = False
    touch_start = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
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

            # touch is delivered as mouse events on Android
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch_start = event.pos
                if not game.alive:
                    game.reset()
                    paused = False
                    touch_start = None
                elif paused:
                    paused = False
                    touch_start = None

            elif event.type == pygame.MOUSEMOTION and touch_start and game.alive:
                dx = event.pos[0] - touch_start[0]
                dy = event.pos[1] - touch_start[1]
                if max(abs(dx), abs(dy)) >= SWIPE_MIN:
                    if abs(dx) > abs(dy):
                        game.turn(RIGHT if dx > 0 else LEFT)
                    else:
                        game.turn(DOWN if dy > 0 else UP)
                    touch_start = event.pos  # allows chained swipes in one touch

            elif event.type == pygame.MOUSEBUTTONUP:
                touch_start = None

        if not paused:
            game.step()
        best = max(best, game.score)

        # ---- draw ----
        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK, (off_x, off_y, cols * cell, rows * cell), 1)
        for x, y in game.body:
            pygame.draw.rect(screen, WHITE, (off_x + x * cell, off_y + y * cell, cell, cell))
        if game.food:
            fx, fy = game.food
            pygame.draw.rect(screen, RED, (off_x + fx * cell, off_y + fy * cell, cell, cell))
        screen.blit(font.render(f"Score: {game.score}", True, WHITE), (12, top_bar // 3))

        if game.alive and not game.started:
            centered(screen, font, "Swipe to start", sh // 2 - font.get_height() // 2, GRAY)
        if not game.alive:
            centered(screen, big, "GAME OVER", sh // 2 - big.get_height())
            centered(screen, font, f"Score: {game.score}   Best: {best}", sh // 2 + 10)
            centered(screen, font, "Tap to restart", sh // 2 + 10 + font.get_height() * 1.5, GRAY)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
