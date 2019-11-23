def distance(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dx, -dx, dy, -dy)


def isYCase(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) > max(dx, -dx)


def getLine(A, B):
    d = distance(A, B)
    p = isYCase(A, B)
    if (not p):
        if (B[1] < A[1]): B, A = A, B
        dx = A[0] - B[0]
        dy = A[1] - B[1]
        dx=max(dx,-dx)
        dy=max(dy,-dy)
        straightLine = [[(B[0]+A[0])/2, A[1] - (dx/2 - dy)], [(B[0]+A[0])/2, B[1] + (dx/2 - dy)]]
        print(straightLine)

getLine([0,0],[8,3])
