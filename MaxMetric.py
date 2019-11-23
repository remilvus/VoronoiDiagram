def distance(A,B):
    dx=A[0]-B[0]
    dy=A[1]-B[1]
    return max(dx,-dx,dy,-dy)
def isYCase(A,B):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return max(dy,-dy)>max(dx,-dx)

def getLine(A,B):
    d=distance(A,B)
    p=isYCase(A,B)
    
    
