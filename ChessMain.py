"""
This is main file for the chess game. Here, we are drawing the board, pieces, and the valid moves.
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import pygame_menu 
import ChessEngine
import ChessAlgo
import sys
from multiprocessing import Process, Queue
from pygame._sdl2.video import Window, WINDOWPOS_CENTERED



boardWidth = boardHeight = moveLogPanelHeight = 512 
moveLogPanelWidth = 200
dimensionOfBoard = 8
sq_size = boardWidth // dimensionOfBoard 


Max_fps = 15 #max frames per second
images={} 



def intiImages():
    """
    To Initialize the images, we need to load them into the dictionary.
    """
    chessPieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for chessPiece in chessPieces:
        images[chessPiece] = pg.transform.scale(pg.image.load("images/" + chessPiece + ".png"),(sq_size,sq_size))



def main():
    """ Main function for the game. """
    pg.init()
    clock = pg.time.Clock()     #to control fps
    screen = pg.display.set_mode((boardWidth + moveLogPanelWidth,boardHeight))
    
    pg.display.set_icon(pg.image.load("./images/chesslogo.ico"))
    pg.display.set_caption("Chess")
    
    

    screen.fill(pg.Color("#4b648a"))    #background color
    gState = ChessEngine.GameState()        #initialize game state
    validMoves = gState.getValidMoves()     #get valid moves
    movesMade = False                   #to check if any move has been made
    animate = False                     #to check if we need to animate a move

    intiImages()                        #initialize images
    running = True                      #to check if the game is running
    sqrSelected = ()                    #to keep track of the square selected
    playerClicks = []                   #to keep track of the player clicks

    gameOverBoard = False
    AIThinking = False
    moveFinderProcess= None
    moveLogFont = pg.font.SysFont("Arial",20, False, False)
    moveUndone = False
    


    while running:
        isHumanTurn = chessPlayerOne if gState.whiteToMove else chessPlayerTwo
        for e in pg.event.get():
            if e.type == pg.QUIT:   #if user clicks on the close button
                pg.quit()
                sys.exit()

            elif e.type  == pg.MOUSEBUTTONDOWN:  #if user clicks on the board``
                if not gameOverBoard and isHumanTurn: 
                    location = pg.mouse.get_pos()
                    col = location[0] // sq_size
                    row = location[1] // sq_size
                    if sqrSelected == (row,col) or col >= 8:
                        sqrSelected = ()
                        playerClicks = []
                    else:
                        sqrSelected = (row,col)
                        playerClicks.append(sqrSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gState.board)
                        
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:                            
                                gState.makeMove(validMoves[i])

                                movesMade = True
                                animate = True
                                sqrSelected = () #reset user clicks 
                                playerClicks = []
                                break
                        else:                       
                            playerClicks = [sqrSelected]
            
            elif e.type == pg.KEYDOWN: 
                # key handling to undo the game by presseing the 'z' key
                if e.key == pg.K_z:         
                    gState.undoLastMove()
                    movesMade = True
                    animate = False
                    gameOverBoard = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                    moveUndone = True
                
                # key handling to reset the game by typing 'r'
                if e.key == pg.K_r:
                    gState = ChessEngine.GameState()
                    validMoves = gState.getValidMoves()
                    movesMade = False
                    animate = False
                    sqrSelected = ()
                    playerClicks = []
                    gameOverBoard = False
                    
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        # AI move finder logic 
        if not gameOverBoard and not isHumanTurn and not moveUndone : 

            if not AIThinking:
                AIThinking = True
                return_queue = Queue()
                moveFinderProcess = Process(target= ChessAlgo.searchBestMoveMinMax, args=(gState,validMoves, return_queue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = return_queue.get()
                if AIMove is None:
                    AIMove = ChessAlgo.searchRandomMove(validMoves)
                gState.makeMove(AIMove)
                movesMade = True
                animate = True
                AIThinking = False

        if movesMade:
            if animate:
                animateMove(gState.moveLog[-1], screen, gState.board, clock)
            validMoves = gState.getValidMoves()
            movesMade = False
            animate = False
            moveUndone = False 
            #drawPlayerTurn(screen,gState.whiteToMove)
        drawGameState(screen, gState, validMoves, sqrSelected)          #draw the game state
        
        if not gameOverBoard:
            drawMoveLog(screen, gState, moveLogFont)
           

        if gState.checkMate:
            gameOverBoard = True
            if gState.whiteToMove:
                screenText(screen, "Black Wins!")
            else:
                screenText(screen, "White Wins!")
        elif gState.staleMate:
             gameOverBoard = True
             screenText(screen, "Stalemate!")
        
        clock.tick(Max_fps)
        pg.display.flip()



def toHighlightSquares(screen, gState, validMoves, sqrSelected):
    """ To highlight the squares selected and the valid moves for the selected chessPiece."""
    
    if (len(gState.moveLog))>0:
        lastMove = gState.moveLog[-1]
        s = pg.Surface((sq_size, sq_size))
        s.set_alpha(100)
        s.fill(pg.Color("#4b648a"))
        screen.blit(s,(lastMove.endCol*sq_size,lastMove.endRow*sq_size))
    if sqrSelected != ():
        r,c = sqrSelected
        if gState.board[r][c][0] == ("w" if gState.whiteToMove else "b"): 

            # To Hightlight selected chessPiece sqaure
            s = pg.Surface((sq_size,sq_size))
            s.set_alpha(150)
            s.fill(pg.Color("#8070a7"))
            screen.blit(s,(c*sq_size,r*sq_size,))

            # To highlight the valid moves for the selected chessPiece
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if move.pieceCaptured != "--":
                        s.fill(pg.Color("#a5554b"))
                    else:
                        s.fill(pg.Color("#97a770"))
                    screen.blit(s,(move.endCol*sq_size,move.endRow*sq_size))



def drawGameState(screen,gState, validMoves, sqrSelected):
    """ Draws the game state on the screen."""
    drawBoard(screen)
    toHighlightSquares(screen,gState,validMoves,sqrSelected)
    drawPieces(screen,gState.board)



def drawBoard(screen):
    '''Draw the squares on the board'''
    global colors 
    colors = [pg.Color("#ECE3D3"),pg.Color("#f9f9f9")]
    #[pg.Color("#d0dff4"),pg.Color("#f9f9f9")]
    #pg.Color("#F2E1C3"),pg.Color("#f8f0e1")
    for i in range(dimensionOfBoard):
        for j in range(dimensionOfBoard):
            color = colors[((i+j)%2)]
            pg.draw.rect(screen,color,pg.Rect(i*sq_size,j*sq_size,sq_size,sq_size))
            


def drawPieces(screen,board):
    """ Draws the chess pieces on the screen."""
    for i in range(dimensionOfBoard):
        for j in range (dimensionOfBoard):
            chessPiece = board[i][j]
            if chessPiece != "--":
                screen.blit(images[chessPiece],pg.Rect(j*sq_size,i*sq_size,sq_size,sq_size))



def drawMoveLog(screen, gState, font):
   
    moveLogRect = pg.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    pg.draw.rect(screen, pg.Color("#D7CFC2"), moveLogRect)
    
    move_Log = gState.moveLog
    moveTexts = []
    for i in range(0, len(move_Log), 2):
        moveString = str(i // 2 + 1) + '. ' + str(move_Log[i]) + "     "
        if i + 1 < len(move_Log):
            moveString += str(move_Log[i + 1]) + "  "
        moveTexts.append(moveString)

    player_one_text = "Human" if chessPlayerOne else "AI"
    player_two_text = "Human" if chessPlayerTwo else "AI"
    text = " {} VS {}".format(player_one_text, player_two_text)
    font = pg.font.SysFont("Arial", 20, True, False)
    text_object = font.render(text, True, pg.Color('#7c634d'))
    text_location = moveLogRect.move(30, 30)
    screen.blit(text_object, text_location)

    movesPerRow = 1
    padding = 15
    line_spacing = 5
    text_y = padding + 80
    moveTexts = moveTexts[-17:]
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        font = pg.font.SysFont("Arial", 15, True, False)
        text_object = font.render(text, True, pg.Color('#3f3752'))
        text_location = moveLogRect.move(padding, text_y)
        screen.blit(text_object, text_location)

        text_y += text_object.get_height() + line_spacing


    
    

def animateMove(move, screen,board, clock):
    global colors
    deltaRow = move.endRow - move.startRow #delta row and col for the animation
    deltaCol = move.endCol - move.startCol
    framesPerSqr = 10 #number of frames per square
    frameCount =  (abs(deltaRow) + abs(deltaCol)) * framesPerSqr #total number of frames
    for frame in range(frameCount + 1):
        r,c = (move.startRow + deltaRow*frame/frameCount, move.startCol +deltaCol*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)

        #erase the piece moved from its ending sqaure
        color = colors[(move.endRow + move.endCol)%2]
        endSqr = pg.Rect(move.endCol*sq_size,move.endRow*sq_size,sq_size,sq_size)
        pg.draw.rect(screen,color,endSqr)        

        if move.pieceCaptured != '--':
            # if move.isEnPassantMove:
            #     enpassantRow = move.endRow+ 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
            #     endSquare = pg.Rect(move.endCol * sq_size, enpassantRow * sq_size, sq_size, sq_size)
            screen.blit(images[move.pieceCaptured], endSqr)
        
        #draw moving piece
        screen.blit(images[move.pieceMoved],pg.Rect(c*sq_size,r*sq_size,sq_size,sq_size))
        pg.display.flip()
        clock.tick(60)






def screenText(screen,text):
    font = pg.font.SysFont("Arial",60, True,False)
    textSurf = font.render(text,True,pg.Color("#a54c4b"))
    textLocation = pg.Rect(0,0, boardWidth, boardHeight).move(boardWidth/2 - textSurf.get_width()/2, boardHeight/2 - textSurf.get_height()/2)
    screen.blit(textSurf,textLocation)



def updatePlayerOne(index, value):
    global chessPlayerOne
    chessPlayerOne = value



def updatePlayerTwo(index, value):
    global chessPlayerTwo
    chessPlayerTwo = value



def frontScreen():
    global chessPlayerOne, chessPlayerTwo
        
    
    chessPlayerOne = True       

    
    chessPlayerTwo = True  
    
    pg.init()
    screen = pg.display.set_mode((boardWidth + moveLogPanelWidth, boardHeight),pg.NOFRAME)
    pg.display.set_icon(pg.image.load("./images/chesslogo.ico"))
    pg.display.set_caption("Chess")
    window = Window.from_display_module()
    window.position = WINDOWPOS_CENTERED
    
                           # add title to the pg window
    
    backgroundmage = pygame_menu.baseimage.BaseImage(
        image_path= "./images/chessmain.png",
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY
    )
    
    theme = pygame_menu.themes.Theme(   title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                                        cursor_color=pg.Color("#3f3752"),
                                        selection_color=pg.Color("#a5554b"),
                                        background_color=backgroundmage,
                                        widget_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                                        widget_font_color=pg.Color("#3f3752"),
                                        widget_font_antialias=True,
                                        widget_selection_effect=pygame_menu.widgets.LeftArrowSelection())

    menu = pygame_menu.Menu(    height=boardHeight, 
                                width= boardWidth + moveLogPanelWidth, 
                                title="", 
                                theme=theme)
    
    menu.add.selector(  'White : ', 
                        [('AI', False), ('Human', True)], 
                        default=chessPlayerOne, 
                        onchange=updatePlayerOne,
                        align=pygame_menu.locals.ALIGN_RIGHT, 
                        font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD, 
                        font_color=pg.Color("#3f3752"), 
                        font_size=18, 
                        margin=(-60, 10))
    
    menu.add.selector(  'Black : ', 
                        [('AI', False), ('Human', True)],
                        default=chessPlayerTwo, 
                        onchange=updatePlayerTwo,
                        align=pygame_menu.locals.ALIGN_RIGHT, 
                        font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD, 
                        font_color=pg.Color("#3f3752"), 
                        font_size=18, 
                        margin=(-60, 10))
    
    menu.add.button(    'Play', 
                        main, 
                        align=pygame_menu.locals.ALIGN_RIGHT, 
                        font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD, 
                        font_color=pg.Color("#3f3752"), 
                        font_size=18, 
                        margin=(-110, 10))
    
    menu.add.button(    'Quit', 
                        sys.exit, 
                        align=pygame_menu.locals.ALIGN_RIGHT, 
                        font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD, 
                        font_color=pg.Color("#3f3752"), 
                        font_size=18, 
                        margin=(-110, 120))
    
    menu.add.label('')

    menu.mainloop(screen)

    pg.display.flip()



if __name__ == "__main__":
    frontScreen()
    
