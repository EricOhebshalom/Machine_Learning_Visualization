import pygame
import random
import sys
import numpy as np

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 200
SQUARE_SIZE = 5
LINE_SPACING = 10
TOP = 20

# Colors
COLOR_ON = (0, 0, 0)       # black squares
COLOR_OFF = (255, 255, 255)  # light gray for off squares
BG_COLOR = (255, 255, 255)   # white background
CURVE_COLOR = (200, 200, 200)

# Original values
ORIGINALM = 1
ORIGINALB = 1
ORIGOLD = 99999999


def draw_lines(screen, line0, line1, curve):
    # Draw zero line
    for idx, value in enumerate(line0):
        color = COLOR_ON if value else COLOR_OFF
        x = idx * SQUARE_SIZE
        y = TOP  # top margin
        pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Draw one line 
    for idx, value in enumerate(line1):
        color = COLOR_ON if value else COLOR_OFF
        x = idx * SQUARE_SIZE
        y = 20 + SQUARE_SIZE + LINE_SPACING * SQUARE_SIZE 
        pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Draw curve line
    for idx, value in enumerate(curve):
        color = CURVE_COLOR
        x = idx * SQUARE_SIZE
        y = TOP + value * SQUARE_SIZE 
        pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

def main():
    m = ORIGINALM
    b = ORIGINALB
    alpha = 0.001
    oldCost = ORIGOLD

    def sigmoidNP(x):
        z = np.clip(m * x + b, -500, 500)
        return 1 / (1 + np.exp(-z))
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Two Lines of Squares")

    # Number of squares per line (fill the width)
    num_squares = SCREEN_WIDTH // SQUARE_SIZE

    #boundary
    boundary = 0

    #bounds for line0
    min0 = 0
    max0 = int(num_squares / 2) - boundary

    #bounds for line1
    min1 = int(num_squares / 2) + boundary
    max1 = int(num_squares)

    # Create boolean lists with 50% chance of being True
    line0 = []
    for i in range(min0, max0):
        line0.append(random.choice([True, False]))
    for i in range(max0, max1):
        line0.append(False)
    line0 = np.array(line0)
    
    

    line1 = []
    for i in range(min0, min1):
        line1.append(False)
    for i in range(min1, max1):
        line1.append(random.choice([True, False]))
    line1 = np.array(line1)
    

    full = np.full_like(line0, fill_value=2, dtype=int)
    full[line0] = 0
    full[line1] = 1
    full[line0 & line1] = 2

    indices = np.arange(len(full))
    mask = (full != 2)
    full_filtered = full[mask]
    x = indices[mask]

    def generateCurve():
        return (LINE_SPACING * (sigmoidNP(indices)) + 0.5)
    curve = generateCurve()

    def lossFunction(): 
        pred = sigmoidNP(x)
        pred[pred == 0] = 1e-15
        pred[pred == 1] = 1 - 1e-15
        completeValues = -(full_filtered * np.log(pred) + (1 - full_filtered) * np.log(1 - pred))
        return np.mean(completeValues)
    
    def derivative(power):
        pred = sigmoidNP(x)
        error = pred - full_filtered
        total = np.sum(error * (x ** power))
        return np.mean(total)
    
    #print(lossFunction())
    stopped = False
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        draw_lines(screen, line0, line1, curve)
        pygame.display.flip()
        if not stopped:
            tempm = m - alpha * derivative(0)
            tempb = b - 2 * alpha * derivative(1)
            m = tempm
            b = tempb
            cost = lossFunction()
            
            if(cost > oldCost):
                oldCost = ORIGOLD
                m = ORIGINALM
                b = ORIGINALB
                alpha /= 2
            elif(abs(cost - oldCost) < 0.000001):
                stopped = True
            else:
                oldCost = cost

            curve = generateCurve()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
