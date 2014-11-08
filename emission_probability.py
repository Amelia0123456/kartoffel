import numpy as np
import math
import db_wrapper
import utils

THRESHOLD_DISTANCE = 50
LWR_TAU = 1
GPS_SIGMA = 3.0


def add_distances(ways, base_point):
    for way in ways:
        way['distances'] = [utils.euclidean_dist(point, base_point) for point in way['points']]
    return ways


def add_tangents(ways):
    for way in ways:
        betas = [lwr(way['points'], index, LWR_TAU) for index in range(len(way['points']))]
        way['angles'] = [math.atan(beta) for beta in betas]
    return ways


def add_tangent_scores(ways, base_angle):
    for way in ways:
        tangent_scores = [math.cos(angle-base_angle)**2 for angle in way['angles']]
        way['tangent_scores'] = tangent_scores
    return ways

def add_distance_scores(ways, sigma):
    p = lambda dist: (1/(math.sqrt(2*math.pi)*sigma))*math.exp(-0.5*(dist/sigma)**2)
    for way in ways:
        way['distance_scores'] = [p(dist) for dist in way['distances']]
    return ways


def lwr(points, index, tau):
    X = np.array([point[0] for point in points], dtype=np.float64)
    X = np.add(X, -np.mean(X))
    X = X.reshape((len(points), 1))
    X = np.concatenate((X, np.ones((len(points),1))), axis=1)
    Y = np.array([point[1] for point in points])
    Y = np.add(Y, -np.mean(Y))
    Y = Y.reshape(len(points), 1)
    w = [math.exp(-utils.euclidean_dist(points[index], points[i])/(2*tau**2)) for i in range(len(points))]
    W = np.diag(w)
    XWXinv = np.linalg.pinv(np.dot(np.dot(X.T, W), X))
    XWY = np.dot(X.T, np.dot(W, Y))
    betas = np.dot(XWXinv, XWY)
    return betas[0][0]


# Takes an array of ways, checks which nodes of the ways are within 'radius' meters of 'base_point'
# Returns array of dicts, where each dict has the osm_id of the way, and the indices of the nodes
# within the radius.
def indices_of_nodes_within_radius(base_point, ways, radius):
    results = []
    for way in ways:
        indices = [point_idx for point_idx, point in enumerate(way['points']) if utils.euclidean_dist(point, base_point) <= radius]
        nodes = {'osm_id': way['osm_id'], 'indices': indices}
        results.append(nodes)
    return results


def test(lat, lon, radius):
    point, ways = db_wrapper.query_ways_within_radius(lat, lon, radius)
    if ways is None or point is None:
        return
    ways = add_distances(ways, point)
    ways = add_tangents(ways)
    ways = add_tangent_scores(ways, 0)
    ways = add_distance_scores(ways, GPS_SIGMA)
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    print pp.pprint(ways)