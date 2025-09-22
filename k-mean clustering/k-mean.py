import numpy as np
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Image dimensions
WIDTH = 500
HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
RED       = (255, 0, 0)
GREEN     = (0, 255, 0)
BLUE      = (0, 0, 255)
YELLOW    = (255, 255, 0)
CYAN      = (0, 255, 255)
MAGENTA   = (255, 0, 255)
ORANGE    = (255, 165, 0)
PURPLE    = (128, 0, 128)
PINK      = (255, 192, 203)
LIME      = (0, 255, 128)
COLORS = np.array([RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, PURPLE, PINK, LIME])
inputSize = 10
SIZE = max(1, min(inputSize, len(COLORS)))

bestCost = float('inf')

#bubbles[i] = [x, y, radius] radius is a variable size
bubbles = np.column_stack((
    np.random.randint(0, WIDTH, SIZE),
    np.random.randint(0, HEIGHT, SIZE),
    np.random.randint(40, 60, SIZE)
))

#dots can only spawn in bubbles
def inBubble(x, y):
    return np.any(np.hypot(bubbles[:,0] - x, bubbles[:,1] - y) < bubbles[:, 2])
    
#generates a batch of invisible color centers. Dots are the color of their closest center 
def newCenters():   
    centers = np.column_stack((np.random.randint(0, WIDTH, SIZE).astype(float),np.random.randint(0, HEIGHT, SIZE).astype(float)))
    return centers[np.argsort(centers[:, 0])]

#a color of a center is their index in COLORS 
centers = newCenters()

# List to hold info about points
allPoints = []
# Populate the array and collect points
for y in range(HEIGHT):
    for x in range(WIDTH):
        if(random.randint(1, 5) == 1 and inBubble(x, y)):

            # Calculate distances from the centers
            dists = np.hypot(centers[:,0] - x, centers[:,1] - y)

            #allPoints[i] = [x, y, closest color center]
            allPoints.append(np.array([x, y, np.argmin(dists)]))

allPoints = np.array(allPoints)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

count = 0

pixelArray = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
# Main loop
while(True):
    oldCost = -1
    cost = 0
    
    #print(np.array_equal(pixelArray, bestPixelArray))
    centers = newCenters()

    #loop until values stop changing
    while abs(cost - oldCost) > 0.0000001:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        #change color values
        x = allPoints[:, 0]
        y = allPoints[:, 1]
        dists = np.hypot(x[:, None] - centers[:, 0], y[:, None] - centers[:, 1])
        min_indices = np.argmin(dists, axis=1)
        pixelArray[y, x] = COLORS[min_indices]
        allPoints[:, 2] = min_indices

        oldCost = cost
        cost = 0

        #find average point, change center values, and gather cost
        for i in range(SIZE): 
            mask = allPoints[:, 2] == i
            centers[i] = [np.mean(allPoints[mask, 0]), np.mean(allPoints[mask, 1])]
            cost += np.sum((np.hypot(centers[i,0] - allPoints[mask, 0], centers[i,1] - allPoints[mask, 1]))**2)
            
        #eliminate invalid values and replace them with a new one
        nanMask = np.isnan(centers[:, 0])
        centers[nanMask] = [random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)]
    '''
    count += 1
    print(count)
    '''
    #update best values and display
    if(cost < bestCost):
        
        bestCost = cost
        #print("centers\n" + str(centers))
        #print("bubbles\n" + str(bubbles))
        
        #render
        surface = pygame.surfarray.make_surface(np.transpose(pixelArray, (1, 0, 2)))
        screen.blit(surface, (0, 0))
        pygame.display.flip()