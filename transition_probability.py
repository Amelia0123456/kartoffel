import math
import utils

BETA = 1.0/2.0

def _compute_distance_scores(segments1, segments2):
    scores = [[] for _ in range(len(segments1))]
    for i, segment1 in enumerate(segments1):
        for segment2 in segments2:
            d1 = utils.point_to_lineseg_dist(segment1, segment2[0])
            d2 = utils.point_to_lineseg_dist(segment1, segment2[1])
            d3 = utils.point_to_lineseg_dist(segment2, segment1[0])
            d4 = utils.point_to_lineseg_dist(segment2, segment1[1])
            dist = min(d1,d2,d3,d4)
            scores[i].append(math.exp(-BETA*dist))
    return scores

def compute_transition_probabilities(segments1, segments2):
    clean_segments1 = [s[2] for s in segments1]
    clean_segments2 = [s[2] for s in segments2]
    scores = _compute_distance_scores(clean_segments1, clean_segments2)
    return scores
