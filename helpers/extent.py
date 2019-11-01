import math

# determin if one extent intersects another


def intersects(extent1, extent2):
    return extent1[0] <= extent2[2] and extent1[2] >= extent2[0] and extent1[1] <= extent2[3] and extent1[3] >= extent2[1]

# get the interesection of two extent


def getIntersection(extent1, extent2):
    intersection = createEmpty()
    if (intersects(extent1, extent2)):
        if (extent1[0] > extent2[0]):
            intersection[0] = extent1[0]
        else:
            intersection[0] = extent2[0]
        if (extent1[1] > extent2[1]):
            intersection[1] = extent1[1]
        else:
            intersection[1] = extent2[1]
        if (extent1[2] < extent2[2]):
            intersection[2] = extent1[2]
        else:
            intersection[2] = extent2[2]
        if (extent1[3] < extent2[3]):
            intersection[3] = extent1[3]
        else:
            intersection[3] = extent2[3]
    return intersection

# create an empty extent


def createEmpty():
    return [math.inf, math.inf, -math.inf, -math.inf]
