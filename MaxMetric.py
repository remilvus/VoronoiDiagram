def distance(A, B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dx, -dx, dy, -dy)




def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


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


# def getLine(A, B): #Returns : [[a],[first_point],[second_point],[a]]
#     if (isXCase(A, B)): #X difference is greater
#         if (B[1] < A[1]): C, D= B, A
#         else: C, D=A, B
#         if (D[0]>C[0]): p=-1
#         else: p=1
#         dx = C[0] - D[0]
#         dy = C[1] - D[1]
#         dx=max(dx,-dx)
#         dy=max(dy,-dy)
#         if(dy==0): straightLine=[[0],[(D[0]+C[0])/2, C[1] - (dx/2 - dy)], [(D[0]+C[0])/2, D[1] + (dx/2 - dy)],[0]]
#         else: straightLine = [[p],[(D[0]+C[0])/2, C[1] - (dx/2 - dy)], [(D[0]+C[0])/2, D[1] + (dx/2 - dy)],[p]]
#     elif(isYCase(A, B)): #Y difference is greater
#         if (B[0] < A[0]): C, D = B, A
#         else: C, D=A, B
#         if (D[1]<C[1]): p=1
#         else: p=-1
#         dx = C[0] - D[0]
#         dy = C[1] - D[1]
#         dx=max(dx,-dx)
#         dy=max(dy,-dy)
#         if(dx==0): straightLine= [[0],[ C[0] - (dy/2 - dx),(D[1]+C[1])/2], [D[0] + (dy/2 - dx),(D[1]+C[1])/2],[0]]
#         else: straightLine = [[p],[ C[0] - (dy/2 - dx),(D[1]+C[1])/2], [D[0] + (dy/2 - dx),(D[1]+C[1])/2],[p]]
#     elif(eqCase(A,B)):
#         if ((B[0] > A[0] and B[1] > A[1])):
#             straightLine=[[-1], [A[0],B[1]],[B[0],A[1]],[-1]]
#         if ((B[0] < A[0] and B[1] < A[1])):
#             straightLine=[[-1], [B[0],A[1]],[A[0],B[1]],[-1]]
#         if ((B[0] < A[0] and B[1] > A[1])):
#             straightLine=[[1], [B[0],A[1]],[A[0],B[1]],[1]]
#         if ((B[0] > A[0] and B[1] < A[1])):
#             straightLine=[[1], [A[0],B[1]],[B[0],A[1]],[1]]
#     print(straightLine)
#     return straightLine


# def getPoints(A,B):
#     output=[]
#     temp=getLine(A,B)
#     if(temp[0][1]==temp[1][1]): return [temp[0], 1], [temp[1], 1]
#     elif(temp[0][1]>temp[1][1]):
#         return [temp[0], 1], [temp[1], 0]
#     elif(temp[0][1]<temp[1][1]):
#         return [temp[0], 0],[temp[1], 1]

def getCross(segment1,segment2):
    t = [[p[1], p[2]]]
    t.append([[1 + p[2][0], p[2][1] + 1 * p[0]], p[2]])
    s=line_intersection([segment1[1],
    t.append([p[1], [p[1][0] - 1, p[1][1] - 1 * p[0]]])
    if(segment1[1][1] == segment1[2][1] and segment2[1][1] == segment2[2][1]):
        # Here if both Y are equal
        cross=line_intersection([segment1[1], if(segment1[1][0]>segment1[1][0])
        y1=segment1[1][1]
        y2=segment2[1][1]
    #
    # elif(segment1[1][1] == segment1[2][1] and segment2[1][0] == segment2[2][0]):
    #     # Here if 1st Y are equal and second X are equal
    #
    # elif(segment1[1][0] == segment1[2][0] and segment2[1][1] == segment2[2][1]):
    #     # Here if 1st X are equal and secon Y are equal
    #
    # elif(segment1[1][0] == segment1[2][0] and segment2[1][0] == segment2[2][0]):
    #     # Here if both X are equal
    return 0

    # else:
    #     print("Error exception found")
    #     print("For ", segment1, "or",segment2,"not Xs nor Ys equals")

getLine([0,0],[8,3])
getLine([0,0],[3,8])

