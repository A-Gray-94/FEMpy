"""
==============================================================================
Mesh Utilities
==============================================================================
@File    :   Mesh.py
@Date    :   2021/04/08
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================

# ==============================================================================
# External Python modules
# ==============================================================================
import numpy as np
from numba import njit

# ==============================================================================
# Extension modules
# ==============================================================================


def makeNodeElsMat(Conn):
    """Generate data structure listing elements connected to each node



    Parameters
    ----------
    Conn : 2D iterable
        Mesh connectivity data, Conn[i][j] is the index of the jth node in the ith element

    Returns
    -------
    nodeEls : list of lists
        List containing indices of each element a node is used by, i.e nodeEls[i] is a list of the elements using node i
    """
    numEl = np.shape(Conn)[0]
    numNode = np.max(Conn) + 1
    nodeEls = [[] for _ in range(numNode)]
    for row in range(numEl):
        for n in Conn[row]:
            nodeEls[n].append(row)
    return nodeEls


def getEdgesfromNodes(nodes, conn, nodeEls, edgeInds):
    """Compute the edges connecting a set of nodes

    Currently assumes all elements are same type

    Parameters
    ----------
    nodes : list or array
        node indices
    conn : 2d array
        Element connectivity matrix
    nodeEls : list of lists
        Node element data structure, generated by `makeNodeElsMat`
    edgeInds : list of lists
        edgeInds[i] contains the local indices of the nodes that make up the ith edge of the element type, for example,
        for a 4 node quad where the nodes are ordered LL, LR, UL, UR, then the bottom, right, upper and left edges are
        given by: edgeInds = [[0, 1], [1, 3], [3, 2], [2, 0]]

    Returns
    -------
    Elements : list
        Indices of elements containing edges described by the node set
    Edges : list of lists
        Edges[i] contains the indices of the edges of Elements[i] in set
    """

    # --- Loop through nodes and create dict with element numbers as keys and element nodes in set as values ---
    elNodes = {}
    for node in nodes:
        els = nodeEls[node]
        for el in els:
            if el in elNodes:
                elNodes[el].append(node)
            else:
                elNodes[el] = [node]

    # --- Now loop through each of the elements we just found that have at least one node in the set and see if the nodes from the set in that element make up any edges ---
    elEdges = {}
    for e in elNodes:
        for j in range(len(edgeInds)):
            locEdgeNodes = edgeInds[j]
            edgeNodes = conn[e][locEdgeNodes]
            if all(i in nodes for i in edgeNodes):
                if e in elEdges:
                    elEdges[e].append(j)
                else:
                    elEdges[e] = [j]
    Elements = []
    Edges = []
    for el, edge in elEdges.items():
        Elements.append(el)
        Edges.append(edge)
    return Elements, Edges


@njit(cache=True)
def computeElementCentroids(nodeCoords, conn):
    """Compute element centroids



    Parameters
    ----------
    nodeCoords : numNode x numDim array
        Element node real coordinates
    conn : 2D iterable
        Mesh connectivity data, Conn[i][j] is the index of the jth node in the ith element

    Returns
    -------
    centroids : numElement x numDim array
        Element centroid coordinates
    """
    centroids = np.zeros((conn.shape[0], np.shape(nodeCoords)[1]))
    for i in range(conn.shape[0]):
        els = conn[i]
        centroids[i] = 1.0 / len(els) * np.sum(nodeCoords[els], axis=0)
    return centroids
