def distance(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dx, -dx, dy, -dy)


def isYCase(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) > max(dx, -dx)

def isXCase(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) < max(dx, -dx)


def getLine(A, B):
    d = distance(A, B)
    p = isXCase(A, B)
    q = isYCase(A, B)
    if (p):
        if (B[1] < A[1]): C, D = B, A
        else: C, D=A, B
        dx = C[0] - D[0]
        dy = C[1] - D[1]
        dx=max(dx,-dx)
        dy=max(dy,-dy)
        straightLine = [[" 45 degrees Right"],[(D[0]+C[0])/2, C[1] - (dx/2 - dy)], [(D[0]+C[0])/2, D[1] + (dx/2 - dy)],["45 degrees Left"]]
        print(straightLine)
    elif(q):
        if (B[0] < A[0]): C, D = B, A
        else: C, D=A, B
        dx = C[0] - D[0]
        dy = C[1] - D[1]
        dx=max(dx,-dx)
        dy=max(dy,-dy)
        straightLine = [[" 45 degrees Left"],[ C[0] - (dy/2 - dx),(D[1]+C[1])/2], [D[0] + (dy/2 - dx),(D[1]+C[1])/2],["45 degrees Right"]]
        print(straightLine)
# def getPoints(A,B):
#     temp=getLine(A,B)
    # if(temp[0][1]==temp[1][1])


getLine([0,0],[8,3])
getLine([0,0],[3,8])

