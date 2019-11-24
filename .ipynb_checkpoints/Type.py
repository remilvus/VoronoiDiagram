
def leftEnd(point ,p ,rangeX ,rangeY):
    x, y =point[0], point[1]
    if (p > 0):  # Jeżeli leci w dół
        if (x - rangeX[0] < y - rangeY[0]):  # Jeżeli zdarzy się z X=0
            dx = x - rangeX[0]
            fx = rangeX[0]
            fy = y - dx
        else:  # Jeżeli się zdrzarzy, że Y=max
            dy = y - rangeY[0]
            fy = rangeY[0]
            fx = x - dy
    elif (p < 0):  # Jeżeli leci w górę
        if (x - rangeX[0] < rangeY[1] - y):  # Zdarzy się x=0
            dx = x - rangeX[0]
            fx = rangeX[0]
            fy = y + dx
        else:  # Jeżeli zdarzy się, ze Y=0
            dy = rangeY[1] - y
            fy = rangeY[1]
            fx = x - dy
    else:
        fy = y
        fx = 0
    return [fx, fy]


def rightEnd(point, p, rangeX, rangeY):
    x, y = point[0], point[1]
    if (p < 0):  # Jeżeli leci w dół
        if (rangeX[1] - x < y - rangeY[0]):  # Jeżeli zdarzy się z X=0
            dx = rangeX[1] - x
            fx = rangeX[1]
            fy = y - dx
        else:  # Jeżeli się zdrzarzy, że Y=max
            dy = y - rangeY[0]
            fy = rangeY[0]
            fx = x + dy
    elif (p > 0):  # Jeżeli leci w górę
        if (rangeX[1] - x < rangeY[1] - y):  # Zdarzy się x=0
            dx = rangeX[1] - x
            fx = rangeX[1]
            fy = y + dx
        else:  # Jeżeli zdarzy się, ze Y=0
            dy = rangeY[1] - y
            fy = rangeY[1]
            fx = x + dy
    else:  # fine
        fy = y
        fx = 0
    return [fx, fy]


def bisector(A, B, rangeX=[0, 1], rangeY=[0, 1]):
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    dx = max(dx, -dx)
    dy = max(dy, -dy)
    if (dx > dy):
        if A[0] > B[0]:
            A[0], A[1], B[0], B[1] = B[0], B[1], A[0], A[1]
        if (dy == 0):  # 1
            return [[[(A[0] + B[0]) / 2, rangeY[0]], [(A[0] + B[0]) / 2, rangeY[1]]]]
        # Linia jest w osi OY. I są punkty załamania
        # [(D[0] + C[0]) / 2, C[1] - (dx / 2 - dy)], [(D[0] + C[0]) / 2, D[1] + (dx / 2 - dy)]

        elif A[1] < B[1]:  # 2
            x = (B[0] + A[0]) / 2
            y1 = B[1] + (dx / 2 - dy)
            y2 = A[1] - (dx / 2 - dy)
            leftPoint = leftEnd([x, y1], -1, rangeX, rangeY)
            rightPoint = rightEnd([x, y2], -1, rangeX, rangeY)
            return [[leftPoint, [x, y1]], [[x, y1], [x, y2]], [[x, y2], rightPoint]]
        else:  # 3
            x = (B[0] + A[0]) / 2
            y1=min(A[1],B[1])
            y2=max(A[1],B[1])
            y2+=  (dx / 2 - dy)
            y1-=  (dx / 2 - dy)
            leftPoint = leftEnd([x, y1], 1, rangeX, rangeY)
            rightPoint = rightEnd([x, y2], 1, rangeX, rangeY)
            return [[leftPoint, [x, y1]], [[x, y1], [x, y2]], [[x, y2], rightPoint]]
    elif dy > dx:
        if A[1] < B[1]:
            A[0], A[1], B[0], B[1] = B[0], B[1], A[0], A[1]
        if (dx == 0):
            return [[[rangeX[0],(A[1]+B[1])/2],[rangeX[1],(A[1]+B[1])/2]]]
        elif A[0] < B[0]:  # 4
            y = (B[1] + A[1]) / 2
            x2 = B[0] + (dy / 2 - dx)
            x1 = A[0] - (dy / 2 - dx)
            leftPoint = leftEnd([x1, y], -1, rangeX, rangeY)
            rightPoint = rightEnd([x2, y], -1, rangeX, rangeY)
            return [[leftPoint, [x1, y]], [[x1, y], [x2, y]], [[x2, y], rightPoint]]
        else:
            y = (B[1] + A[1]) / 2  # 5
            x1 = B[0] - (dy / 2 - dx)
            x2 = A[0] + (dy / 2 - dx)
            leftPoint = leftEnd([x1, y], 1, rangeX, rangeY)
            rightPoint = rightEnd([x2, y], 1, rangeX, rangeY)
            return [[leftPoint, [x1, y]], [[x1, y], [x2, y]], [[x2, y], rightPoint]]
    else:
        if A[1] > B[1] and A[0] < B[0]:  # 6
            x = (B[0] + A[0]) / 2
            y = (B[1] + A[1]) / 2
            leftPoint = leftEnd([x, y], 1, rangeX, rangeY)
            rightPoint = rightEnd([x, y], 1, rangeX, rangeY)
            return [[leftPoint, rightPoint]]
        else:  # 7
            x = (B[0] + A[0]) / 2
            y = (B[1] + A[1]) / 2
            leftPoint = leftEnd([x, y], -1, rangeX, rangeY)
            rightPoint = rightEnd([x, y], -1, rangeX, rangeY)
            return [[leftPoint, rightPoint]]
