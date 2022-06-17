import random
from math import inf

pieceChessScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

checkMatePoint = inf 
staleMatePoint = 0
depth = 3

scoresOfQueen = [[0.0,   0.2,    0.2,    0.3,    0.3,    0.2,    0.2,    0.0],
                [0.2,   0.4,    0.4,    0.4,    0.4,    0.4,    0.4,    0.2],
                [0.2,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.2],
                [0.3,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.3],
                [0.4,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.3],
                [0.2,   0.5,    0.5,    0.5,    0.5,    0.5,    0.4,    0.2],
                [0.2,   0.4,    0.5,    0.4,    0.4,    0.4,    0.4,    0.2],
                [0.0,   0.2,    0.2,    0.3,    0.3,    0.2,    0.2,    0.0]]

scoresOfKnight = [[0.0,  0.1,    0.2,    0.2,    0.2,    0.2,    0.1,    0.0],
                 [0.1,  0.3,    0.5,    0.5,    0.5,    0.5,    0.3,    0.1],
                 [0.2,  0.5,    0.6,    0.65,   0.65,   0.6,    0.5,    0.2],
                 [0.2,  0.55,   0.65,   0.7,    0.7,    0.65,   0.55,   0.2],
                 [0.2,  0.5,    0.65,   0.7,    0.7,    0.65,   0.5,    0.2],
                 [0.2,  0.55,   0.6,    0.65,   0.65,   0.6,    0.55,   0.2],
                 [0.1,  0.3,    0.5,    0.55,   0.55,   0.5,    0.3,    0.1],
                 [0.0,  0.1,    0.2,    0.2,    0.2,    0.2,    0.1,    0.0]]

scoresOfBishop = [[0.0,  0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.0],
                 [0.2,  0.4,    0.4,    0.4,    0.4,    0.4,    0.4,    0.2],
                 [0.2,  0.4,    0.5,    0.6,    0.6,    0.5,    0.4,    0.2],
                 [0.2,  0.5,    0.5,    0.6,    0.6,    0.5,    0.5,    0.2],
                 [0.2,  0.4,    0.6,    0.6,    0.6,    0.6,    0.4,    0.2],
                 [0.2,  0.6,    0.6,    0.6,    0.6,    0.6,    0.6,    0.2],
                 [0.2,  0.5,    0.4,    0.4,    0.4,    0.4,    0.5,    0.2],
                 [0.0,  0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.0]]

scoresOfRook = [[0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.25],
               [0.5,    0.75,   0.75,   0.75,   0.75,   0.75,   0.75,   0.5],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,  0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.25,   0.25,   0.25,   0.5,    0.5,    0.25,   0.25,   0.25]]

scoresOfPawn = [[0.8,    0.8,    0.8,    0.8,    0.8,    0.8,    0.8,    0.8],
               [0.7,    0.7,    0.7,    0.7,    0.7,    0.7,    0.7,    0.7],
               [0.3,    0.3,    0.4,    0.5,    0.5,    0.4,    0.3,    0.3],
               [0.25,   0.25,   0.3,    0.45,   0.45,   0.3,    0.25,   0.25],
               [0.2,    0.2,    0.2,    0.4,    0.4,    0.2,    0.2,    0.2],
               [0.25,   0.15,   0.1,    0.2,    0.2,    0.1,    0.15,   0.25],
               [0.25,   0.3,    0.3,    0.0,    0.0,    0.3,    0.3,    0.25],
               [0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2]]

piecePositionScores = {  "wN": scoresOfKnight, "bN": scoresOfKnight[::-1],
                         "wB": scoresOfBishop, "bB": scoresOfBishop[::-1],
                         "wQ": scoresOfQueen,  "bQ": scoresOfQueen[::-1],                        
                         "wR": scoresOfRook,   "bR": scoresOfRook[::-1],
                         "wP": scoresOfPawn,   "bP": scoresOfPawn[::-1]}



def scoreOfBoard(gState):
    ''' A positive score means white is winning. and vice versa '''
    if gState.checkMate:
        if gState.whiteToMove:
            return -checkMatePoint # black is winning
        else:
            return checkMatePoint # white is winning
    elif gState.staleMate:
        return staleMatePoint # stalemate

    score = 0

    for row in range(len(gState.board)):
        for col in range(len(gState.board[row])):
            piece = gState.board[row][col]
            if piece != '--':
                piecePositionScore = 0
                if piece[1] != 'K':
                    piecePositionScore = piecePositionScores[piece][row][col]
                if piece[0] == 'w':
                    score += pieceChessScore[piece[1]] + piecePositionScore
                elif piece[0] == 'b':
                    score -= pieceChessScore[piece[1]] + piecePositionScore
    return score



def searchRandomMove(validMoves):
    #find a random move from the list of valid moves
    return random.choice(validMoves)



def searchBestMoveMinMax(gState,validMoves, return_queue):
    """helper method to make first recursive call"""
    global upcomingMove

    upcomingMove = None
    random.shuffle(validMoves)

    searchMinMaxAlphaBetaMove(gState, validMoves, depth, -checkMatePoint, checkMatePoint, gState.whiteToMove)

    return_queue.put(upcomingMove)



def searchMinMAxMove(gState,validMoves, Depth, whiteToMove):
    global upcomingMove 
    if Depth == 0: 
        return scoreOfBoard(gState)
        
    if whiteToMove:
        maxScore = -checkMatePoint
        for  move in validMoves:

            gState.makeMove(move)
            upcomingMoves = gState.getValidMoves()
            score = searchMinMAxMove(gState, upcomingMoves, Depth-1, False)

            if score > maxScore:
                maxScore = score
                if Depth == depth:
                    upcomingMove = move

            gState.undoLastMove()

        return maxScore
    
    else:
        minScore = checkMatePoint

        for move in validMoves:

            gState.makeMove(move)
            upcomingMoves = gState.getValidMoves()
            score = searchMinMAxMove(gState, upcomingMoves, Depth-1, True)

            if score < minScore:
                minScore = score
                if Depth == depth:
                    upcomingMove = move
            gState.undoLastMove()
        return minScore 



def searchMinMaxAlphaBetaMove(gState, validMoves, Depth, alpha, beta, maxPlayer):

    global upcomingMove

    if Depth == 0: 
        return scoreOfBoard(gState)
    
    if maxPlayer:
        maxScore = -checkMatePoint

        for  move in validMoves:
            gState.makeMove(move)
            upcomingMoves = gState.getValidMoves()
            cscore = searchMinMaxAlphaBetaMove(gState, upcomingMoves, Depth-1, alpha, beta, False)

            if cscore > maxScore:
                maxScore = cscore
                if Depth == depth:
                    upcomingMove = move
            
            gState.undoLastMove()

            alpha = max(alpha, maxScore)
            if beta <= alpha:
                break
        return maxScore
    
    else:
        minScore = checkMatePoint

        for move in validMoves:
            gState.makeMove(move)
            upcomingMoves = gState.getValidMoves()
            cscore = searchMinMaxAlphaBetaMove(gState, upcomingMoves, Depth-1, alpha, beta, True)

            if cscore < minScore:
                minScore = cscore
                if Depth == depth:
                    upcomingMove = move
            gState.undoLastMove()

            beta = min(beta, minScore)
            if beta <= alpha:
                break
        return minScore
        
