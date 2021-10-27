import math
import numpy as np

def final_distance(x):
    final=[]
    for count,ii in enumerate(x):
        for points in  ii:
            final.append(points)
        dist=distance_formula_single_index(x,count)
            #print(dist)
        for d in dist:
            final.append(d)
    return np.array(final)

def distance_formula_single_index(x,i):
    distance=[]
    for j,k in enumerate(x):
        dist=[]
        if j==i:
            continue
        if j>i:
            point1 = np.array(x[i])
            point2 = np.array(k)
            # finding sum of squares
            sum_sq = np.sum(np.square(point1 - point2))
            distance.append(np.sqrt(sum_sq))
        #distance.append(dist)
    # Doing squareroot and
    # printing Euclidean distance
    return distance

def angle_calc(x,i):
    j=0
    
    angles=[]
    for j,k in enumerate(x):
        dist=[]
        if j==i:
            continue
        if j>i:
            point1 = tuple(x[i])
            #print(point1)

            point2=tuple(x[i+1])
            point3 = tuple(k)
            # finding sum of squares
            angles.append(getAngle(point1,point2,point3))
    return angles

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang


def final_points(dist_points,val):
    angles_list=[]
    for k,t in enumerate(val):
        angles=angle_calc(val,k)
        if angles:
            angles_list.extend(angles)
    return np.concatenate((dist_points,np.array(angles_list)))
    
    
   