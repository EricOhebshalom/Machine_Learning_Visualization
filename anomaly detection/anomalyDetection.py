import pygame
import numpy as np
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 900
HEIGHT = 700

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("anomaly detection")

pixels = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)  # RGB black

#bubble = [x, y, radius]
bubble = np.array((
    np.random.randint(0, WIDTH),
    np.random.randint(0, HEIGHT),
    np.random.randint(0, min(WIDTH/3, HEIGHT/3))
))

def inBubble(x, y):
    return True
    return np.hypot(bubble[0] - x, bubble[1] - y) < bubble[2]

sigma = bubble[2]
sigmaSquare = bubble[2]**2

goodExamples = []

for x in range(WIDTH):
    for y in range(HEIGHT):
        distance = np.hypot(x - bubble[0], y - bubble[1])
        probability = math.exp((-(distance**2) / (sigmaSquare)))
        if random.random() < probability and inBubble(x, y):          
            pixels[x][y] = WHITE
            goodExamples.append(np.array([x, y]))
goodExamples = np.array(goodExamples)


muX = np.mean(goodExamples[:, 0])
muY = np.mean(goodExamples[:, 1])

sigmaXsquare = np.mean((goodExamples[:, 0] - muX)**2)
sigmaYsquare = np.mean((goodExamples[:, 1] - muY)**2)

sigmaX = np.sqrt(sigmaXsquare)
sigmaY = np.sqrt(sigmaYsquare)

sqrtX = 1/((math.sqrt(2 * math.pi)) * sigmaX)
sqrtY = 1/((math.sqrt(2 * math.pi)) * sigmaY)

# Convert array to surface and draw
surface = pygame.surfarray.make_surface(pixels)
screen.blit(surface, (0, 0))
pygame.display.flip()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            print("X pos: " + str(x))
            print("Y pos: " + str(y))
            newX = sqrtX * math.exp(-1 * (((x - muX)**2)/(2*sigmaXsquare)))
            newY = sqrtY * math.exp(-1 * (((y - muY)**2)/(2*sigmaYsquare)))
            
            print(format(newX * newY, 'f'))
            if((newX * newY > 0.000001)):
                print("safe")
            else:
                print("anomaly detected")
            '''
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                pixels[x, y] = WHITE  # set clicked pixel to white'''

    

