import pygame
import sys
import random
import numpy as np
import pyperclip

ROWS = 100
COLS = 100
CARR = np.arange(COLS)

#if true visualize with pygame but much slower. If false use terminal and pyperclip  
DISPLAY = True

#degree is 1 below size. For example size 2 is linear and size 3 is quadratic 
STARTING_SIZE = 2

#Display Constants
CELL_SIZE = 8
BACKGROUND = (255, 255, 255)  # white
CURVE = (150, 150, 150)  # gray
BOTH = (75, 75, 75) # dark gray
DOTS = (0, 0, 0) #black

#gather data
isGood = [[False for _ in range(ROWS)] for _ in range(COLS)]
dataList = []
while(len(dataList) == 0):
    gen = 0
    while(gen == 0):
        gen = random.randint(-COLS, COLS)
    
    #upper bound
    upperM = random.randint(-COLS, COLS)/gen
    upperB = random.randint(0, COLS)

    gen = 0 
    while(gen == 0):
        gen = random.randint(-COLS, COLS)
    #lower bound
    lowerM = random.randint(-COLS, COLS)/gen
    lowerB = random.randint(0, COLS)

    for col in range(COLS):
        for row in range(ROWS):
            if(row - (upperM * col + upperB) > 0) and (row - (lowerM * col + lowerB) < 0) and random.randint(1, 10) == 1:
                dataList.append([col, row])
                isGood[col][row] = True

npData = np.array(dataList)
X = npData[:,0]  # all x (col)
Y = npData[:,1] 

#main method
def main(size):
    def printAndCopy(testAll):
        
        terms = []
        for i, coeff in enumerate(testAll):
            terms.append(f"({coeff:.20f})x^{i}")
        
        #content can easily be pasted onto desmos
        content = " + ".join(terms)
        print(content)
        pyperclip.copy(content)

    #array of numbers from 0 to size - 1
    exp = np.arange(size)

    def prediction(testAll):
        return np.sum(testAll * (X[:, np.newaxis] ** exp), axis=1)

    testAll = np.zeros(size)
    
    def getDerivative(degree):
        return np.mean((prediction(testAll) - Y) * (X**degree))
    
    def get_cost():
        errors = prediction(testAll) - Y
        return np.mean(errors**2) / 2

    def draw_board(screen, board):
        """Draw the checkerboard on the screen from the 2D array."""
        for col in range(len(board)):
            for row in range(len(board[col])):
                color = board[col][row]
                rect = pygame.Rect((col ) * CELL_SIZE, (ROWS - 1 - row) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)


    if DISPLAY:
        pygame.init()
        screen = pygame.display.set_mode((COLS * CELL_SIZE, ROWS * CELL_SIZE))
        pygame.display.set_caption("Regression with degree " + str(size - 1))
    
        board = []
        for col in range(COLS):
            board_col = []
            for row in range(ROWS):
                color = BACKGROUND
                if(isGood[col][row]):
                    color = DOTS
                board_col.append(color)
            board.append(np.array(board_col))
        board = np.array(board)
        
        def create_checkerboard(board):
            newBoard = board.copy()
            
            bestInds = np.sum(testAll * (CARR[:, np.newaxis] ** exp), axis=1) + 0.5
            bestInds = bestInds.astype(int)
            valid = (bestInds >= 0) & (bestInds < ROWS)
            
            background_values = newBoard[CARR[valid], bestInds[valid], 0]
            is_background = background_values == BACKGROUND[0]
            
            newBoard[CARR[valid][is_background], bestInds[valid][is_background]] = CURVE
            newBoard[CARR[valid][~is_background], bestInds[valid][~is_background]] = BOTH
            
            return newBoard 

    running = True
    #alpha
    alphaB = 0.99
    alphas = np.full(size, alphaB)
    #cost
    startOldCost = 99999
    oldCost = startOldCost
    #count and tolerance
    count = 0
    #refresh rate
    REFRESH = 1000
    reset = False
    while running:
        #update testAll 
        derivatives = np.vectorize(getDerivative)(exp)
        testAll = testAll - alphas * derivatives

        #reset if cost grows
        cost = get_cost()
        if(cost > oldCost):
            if(reset):
                testAll = np.zeros(size)
                testAll[0] = COLS/2
                reset = False
            else:
                reset = True
        
            #alphas /= (((exp) + 1))
            alphas *= (1 - ((exp) * 0.01))

            #printAndCopy(alphas)
            oldCost = startOldCost
        else:  
            oldCost = cost
            reset = False
        
        #Display or print after enough cycles    
        count += 1
        if count % REFRESH == 0:         
            printAndCopy(alphas)
            printAndCopy(testAll)
            if DISPLAY:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    #left click to increase degree and right click to decrease
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if(event.button == 1):
                            pygame.quit()
                            main(size + 1)
                        elif(event.button == 3):
                            pygame.quit()
                            main(max(size - 1, 1))                
                #create and draw board
                newBoard = create_checkerboard(board)
                screen.fill((0, 0, 0)) 
                draw_board(screen, newBoard) 
                pygame.display.flip()
    if DISPLAY:
        pygame.quit()
        sys.exit()
#Not allowed to call with negative degree
main(max(STARTING_SIZE, 1))
