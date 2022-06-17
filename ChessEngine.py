"""
This class is responsible for storing the chess board and the pieces on it. It will also be responsible for determining the valid moves at the current state of the board.
"""

class GameState():

    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents color of the piece, the second character represents the piece type.
        # "--" is an empty space with no piece on it.

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]            
        ]

        # To check if AI gives Optimum solution
        # self.board = [                                                  
        #     ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        #     ["bP", "bP", "bP", "bP", "bP", "--", "--", "bP"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "bP", "bP", "--"],
        #     ["--", "--", "--", "--", "--", "wP", "--", "--"],
        #     ["--", "--", "--", "--", "wP", "--", "--", "--"],
        #     ["wP", "wP", "wP", "wP", "--", "--", "wP", "wP"],
        #     ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"] 
        # ]


        self.moveFuntions = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves, "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True         # True if white to move, False if black to move
        self.moveLog = []               # list of moves made so far
        self.whiteKingLocation = (7,4)  # location of white king
        self.blackKingLocation =(0,4)   # location of black king
        self.inChecks = False           
        self.checkMate = False           
        self.staleMate = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightLog = [CastleRights(    self.currentCastlingRight.wks, 
                                                self.currentCastlingRight.bks, 
                                                self.currentCastlingRight.wqs, 
                                                self.currentCastlingRight.bqs)]



    def makeMove(self, move):
        """ Make a move on the board """

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)                   #log the move
        self.whiteToMove = not self.whiteToMove     #swap player

        # update king's position
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
            
        # id pawn promotion change piece
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # if enpassant move, must update the board to capture the pawn
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'
            
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow+ move.endRow)//2 , move.startCol)
        else:
            self.enpassantPossible = ()
            
        self.enpassantPossibleLog.append(self.enpassantPossible)
        

        #update castling rights
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:                                                              
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]         
                self.board[move.endRow][move.endCol + 1] = '--'                                             
            else:                                                                                               
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]        
                self.board[move.endRow][move.endCol - 2] = '--'                                              


        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights( self.currentCastlingRight.wks, 
                                                    self.currentCastlingRight.bks,
                                                    self.currentCastlingRight.wqs, 
                                                    self.currentCastlingRight.bqs))
 

   
    def undoLastMove(self):
        """
        undo the last move made"""
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            #update king's position
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo enpassant is different
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            
            
            self.castleRightLog.pop()                                
            self.currentCastlingRight = self.castleRightLog[-1]   
            
            # undo castling move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False 
            self.staleMate = False



    def updateCastleRights(self, move):
        """ Update the castle rights for the given move """

        # If the rook has been captured or moved, remove the castling right
        if move.pieceCaptured == "wR":
            if move.endCol == 0:                               # if rook is on the left side
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:                             # if rook is on the right side
                self.currentCastlingRight.wks = False

        elif move.pieceCaptured == "bR":
            if move.endCol == 0:                               # if rook is on the left side
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:                             # if rook is on the right side
                self.currentCastlingRight.bks = False

        # If rook or king has been moved, remove the castling right
        if move.pieceMoved == 'wK':                            # if white king has been moved then no castling rights
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bK':                          # if black king has been moved then no castling rights
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False

        elif move.pieceMoved == 'wR':                          # if white rook has been moved then no castling rights
            if move.startRow == 7:
                if move.startCol == 0:                         # if rook is on the left side
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:                       # if rook is on the right side
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bR':                          # if black rook has been moved then no castling rights
            if move.startRow == 0:
                if move.startCol == 0:                         # if rook is on the left side
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:                       # if rook is on the right side
                    self.currentCastlingRight.bks = False

    

    def getValidMoves(self):
        """
        All Moves condsidering checks"""
        tempCastleRights = CastleRights(  self.currentCastlingRight.wks, 
                                            self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, 
                                            self.currentCastlingRight.bqs)
        moves = []
        self.inChecks, self.pins, self.checks = self.checkForPinsAndCheks()
        
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inChecks:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()  

            king = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
            self.getCastleMoves(king[0], king[1], moves)
        
        if len(moves) == 0:
            if self.isCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.currentCastlingRight = tempCastleRights

        return moves
            
   

    def getAllPossibleMoves(self):
        """
        All moves without considering checks"""
        moves = []
        for rows in range(len(self.board)):
            for cols in range(len(self.board[rows])):
                turn = self.board[rows][cols][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):                                     
                    piece = self.board[rows][cols][1]
                    self.moveFuntions[piece](rows,cols,moves)   #call the function for the piece
        return moves
    

    
    def getPawnMoves(self,row,col,moves):
        """
        Get all the pawn moves for the pawn located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
                    
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[row + moveAmount][col] == "--":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row + moveAmount, col), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))
                    
        if col - 1 >= 0:  # capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board))

                if (row + moveAmount, col - 1) == self.enpassantPossible:
                    attackingPiece = blokcingPiece = False

                    if kingRow == row:
                        if kingCol < col:  # king is left of the pawn
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:  # king right of the pawn
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blokcingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blokcingPiece = True
                    if not attackingPiece or blokcingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnPassantMove=True))
                        
        if col + 1 <= 7:  # capture to the right
            if not piecePinned or pinDirection == (moveAmount, +1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board))
                elif (row + moveAmount, col + 1) == self.enpassantPossible:
                    attackingPiece = blokcingPiece = False
                    if kingRow == row:
                        if kingCol < col:  
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:  # king right of the pawn
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blokcingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blokcingPiece = True
                    if not attackingPiece or blokcingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnPassantMove=True))


    

    
    def getRookMoves(self,r,c,moves):
        """
        Get all the rook moves for the rook located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece  = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    

    
    def getKnightMoves(self,r,c,moves):
        """
        Get all the knight moves for the knight located at row, col and add these moves to the list"""
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        allyColor = "w" if self.whiteToMove else "b"
        for m in directions:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]  
                    if endPiece[0] !=  allyColor:
                        moves.append(Move((r,c),(endRow,endCol), self.board))


    
    def getBishopMoves(self,r,c,moves):
        """
        Get all the bishop moves for the bishop located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions= ((1,1),(-1,1),(1,-1),(-1,-1))
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                            break
                        else:
                            break
                else:
                    break


    
    def getQueenMoves(self,r,c,moves):
        """
        Get all the queen moves for the queen located at row, col and add these moves to the list"""
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)


    
    def getKingMoves(self,r,c,moves):
        """
        Get all the king moves for the king located at row, col and add these moves to the list"""
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inChecks, pins, checks = self.checkForPinsAndCheks()
                    if not inChecks:
                        moves.append(Move((r,c),(endRow,endCol), self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)



    def isCheck(self):
        """ Determine if a current player is in check """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
        


    def squareUnderAttack(self, row, col):
        """ Determine if enemy can attack the square row col """

        self.whiteToMove = not self.whiteToMove          # switch to other player view
        opponentsMoves = self.getAllPossibleMoves()

        self.whiteToMove = not self.whiteToMove           # switch back to your own view
        for move in opponentsMoves:
            if move.endRow == row and move.endCol == col:     # sqaure is attacked
                return True
        return False



    def checkForPinsAndCheks(self):
        pins = []
        checks = []
        inChecks = False
        if self.whiteToMove:
            allyColor = "w"
            enemyColor = "b"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            allyColor = "b"
            enemyColor = "w"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow,endCol,d[0],d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if  (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():
                                inChecks = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        #check for knight checks
        knightMoves = ((-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inChecks = True
                    checks.append((endRow,endCol,m[0],m[1]))
                    
        return inChecks, pins, checks



    def getCastleMoves(self, row, col, moves):
        """ Generate all valid castle moves for the king at (row, col) and add them to the list of moves. """
        
        if self.squareUnderAttack(row, col): return                                  # can't castle while in check

        if  (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(row, col, moves)

        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(row, col, moves)



    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--' and \
          not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))



    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--' and \
          not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
            moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))



class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self,startSq,endSq,board, isEnPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        
        #en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        

        # castle move
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow*1000 + self.startCol * 100 + self.endRow *10 + self.endCol
        

    
    def __eq__(self, other):
        """
        Overriding the equals methods"""
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        # you can add to make this like real chess notation 
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)


    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    
    def __str__(self):
        # Overriding the string method
        # Castle Move
        if self.isCastleMove: 
            return "0-0" if self.endCol == 6 else "0-0-0"

        endSqaure = self.getRankFile(self.endRow, self.endCol)

        moveString = self.pieceMoved[1]
        if self.isCapture: moveString += "x"
        return moveString + endSqaure