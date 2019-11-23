def distance(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dx, -dx, dy, -dy)


def isYCase(A, B): #Y difference is greater
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) > max(dx, -dx)

def isXCase(A, B): #X difference is greater
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) < max(dx, -dx)
def eqCase(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy, -dy) == max(dx, -dx)


def getLine(A, B):
    d = distance(A, B)
    if (isXCase(A, B)): #X difference is greater
        if (B[1] < A[1]): C, D = B, A
        else: C, D=A, B
        dx = C[0] - D[0]
        dy = C[1] - D[1]
        dx=max(dx,-dx)
        dy=max(dy,-dy)
        if(dy==0): straightLine=[[0],[(D[0]+C[0])/2, C[1] - (dx/2 - dy)], [(D[0]+C[0])/2, D[1] + (dx/2 - dy)],[0]]
        else: straightLine = [[" 45 degrees Right"],[(D[0]+C[0])/2, C[1] - (dx/2 - dy)], [(D[0]+C[0])/2, D[1] + (dx/2 - dy)],["45 degrees Left"]]
        print(straightLine)
    elif(isYCase(A, B)): #Y difference is greater
        if (B[0] < A[0]): C, D = B, A
        else: C, D=A, B
        dx = C[0] - D[0]
        dy = C[1] - D[1]
        dx=max(dx,-dx)
        dy=max(dy,-dy)
        if(dx==0): straightLine= [[0],[ C[0] - (dy/2 - dx),(D[1]+C[1])/2], [D[0] + (dy/2 - dx),(D[1]+C[1])/2],[0]]
        else: straightLine = [[" 45 degrees Left"],[ C[0] - (dy/2 - dx),(D[1]+C[1])/2], [D[0] + (dy/2 - dx),(D[1]+C[1])/2],["45 degrees Right"]]
        print(straightLine)
    elif(eqCase(A,B)):
        if ((B[0] > A[0] and B[1]> A[1])):
            
        straightLine=[[0]]

def getPoints(A,B):
    output=[]
    temp=getLine(A,B)
    if(temp[0][1]==temp[1][1]): return [temp[0], 1], [temp[1], 1]
    elif(temp[0][1]>temp[1][1]):
        return [temp[0], 1], [temp[1], 0]
    elif(temp[0][1]<temp[1][1]):
        return [temp[0], 0],[temp[1], 1]

def getCross(segment1,segment2):
    # if(segment1[1][1] == segment1[2][1] and segment2[1][1] == segment2[2][1]):
    #     # Here if both Y are equal
    #     y1=segment1[1][1]
    #     y2=segment2[1][1]
    #
    # elif(segment1[1][1] == segment1[2][1] and segment2[1][0] == segment2[2][0]):
    #     # Here if 1st Y are equal and second X are equal
    #
    # elif(segment1[1][0] == segment1[2][0] and segment2[1][1] == segment2[2][1]):
    #     # Here if 1st X are equal and secon Y are equal
    #
    # elif(segment1[1][0] == segment1[2][0] and segment2[1][0] == segment2[2][0]):
    #     # Here if both X are equal

    else:
        print("Error exception found")
        print("For ", segment1, "or",segment2,"not Xs nor Ys equals")

getLine([0,0],[8,3])
getLine([0,0],[3,8])

