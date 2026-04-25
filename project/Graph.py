#! /usr/bin/env python

import random
import math
import pulp

def randomSpanningTree( vertices ):
    """Returns an edge set of a random spanning tree on vertices.
    
    Each new vertex is added as a child of a vertex that was already added.  Therefore,
    the maximum degree of this tree tends to log(n).
    """
    edges = []
    unusedVertices = list(vertices)
    random.shuffle( unusedVertices )
    firstUsed = unusedVertices.pop()
    usedVertices = [ firstUsed ]
    while len( unusedVertices ):
        nextVertex = unusedVertices.pop()
        edges.append( ( random.choice( usedVertices ), nextVertex ) )
        usedVertices.append( nextVertex )
    return edges

def randomDisjointPaths( pairs, otherVertices ):
    """Returns an edge set of disjoint paths, one for each pair.
    
    pairs: a list of tuples, as [(source vertex, sink vertex)]
    otherVertices: a list of integers, as [vertex1, vertex2]"""

    edges = []
    paths = [ [] for pair in pairs ]
    unusedVertices = list( otherVertices )
    random.shuffle( unusedVertices )
    for path in paths:
        guaranteedVertex = unusedVertices.pop()
        path.append( guaranteedVertex )
    for vertex in unusedVertices:
        random.choice( paths ).append( vertex )

    for pair in pairs: print( pair )
    print(paths)

    # Starting edge from the source.
    edges += [ ( pair[0], path[0] ) 
               for pair,path 
               in zip( pairs, paths ) ]
    #Intermediate edges for each path.
    for path in paths:
        edges += [ (tail, head)
                   for tail, head
                   in zip( path[:-1],path[1:])]
    # Finishing edge to the sink.
    edges += [ ( path[-1], pair[1] ) 
               for pair,path 
               in zip( pairs, paths ) ]
    
    return edges

def lpSolveDp( pairs, edges ):
    """Solve disjoint-paths using integer programming.
    
    pairs: a list of tuples, as [(source vertex, sink vertex)]
    edges: a list of tuples, as [(tail vertex, head vertex)]
    """

    print( "Edges:", edges )
    prob = pulp.LpProblem( "DisjointPaths", pulp.LpMinimize )

    # The fundamental variables are "is this edge used by this path", which is binary.
    vars = {}
    for edge in edges:
        for iPair in range(len(pairs)):
            vars[edge[0], edge[1], iPair ] = pulp.LpVariable( f"from_{edge[0]}_to_{edge[1]}_path_{iPair}", cat = pulp.LpBinary )

    # We're indifferent as to size, but it might be easier for
    # the optimizer if it tries to minimize total path length used.
    prob += pulp.lpSum( vars )

    # For each source, its outgoing value must be 1 for its path and 0 for all others.
    for thisPair, pair in enumerate( pairs ):
        source = pair[0]
        outEdges = [ edge for edge in edges
                    if edge[0] == source ]
        for iPair in range(len(pairs)):
            outEdgeVars = [ vars[tail,head,iPair] for tail,head in outEdges ]
            if iPair == thisPair:
                prob += pulp.lpSum(outEdgeVars) == 1
            else:
                prob += pulp.lpSum(outEdgeVars) == 0

    # For each sink, its incoming value must be 1 for its path and 0 for all others.
    for thisPair, pair in enumerate( pairs ):
        sink = pair[1]
        inEdges = [ edge for edge in edges
                    if edge[1] == sink ]
        for iPair in range(len(pairs)):
            inEdgeVars = [ vars[tail,head,iPair] for tail,head in inEdges ]
            if iPair == thisPair:
                prob += pulp.lpSum(inEdgeVars) == 1
            else:
                prob += pulp.lpSum(inEdgeVars) == 0

    # For intermediate vertices, its incoming value must equal its outgoing value
    # for all paths.
    endpoints = set([pair[0] for pair in pairs] + [pair[1] for pair in pairs])
    vertices = set([edge[0] for edge in edges] + [edge[1] for edge in edges])
    intermediates = vertices - endpoints
    
    for vertex in intermediates:
        inEdges = [ edge for edge in edges
                    if edge[1] == vertex ]                
        outEdges = [ edge for edge in edges
                    if edge[0] == vertex ]
        # Incoming and outgoing usage must be the same for each path.
        for iPair in range(len(pairs)):
            inEdgeVars = [ vars[tail,head,iPair] for tail,head in inEdges ]
            outEdgeVars = [ vars[tail,head,iPair] for tail,head in outEdges ]
            prob += pulp.lpSum(inEdgeVars) - pulp.lpSum(outEdgeVars) == 0
        # Incoming path usage must be at most 1.
        allInEdgeVars = []
        for iPair in range(len(pairs)):
            allInEdgeVars += [ vars[tail,head,iPair] for tail,head in inEdges ]
        prob += pulp.lpSum( allInEdgeVars ) <= 1

    status = prob.solve()
    print( pulp.LpStatus[status] )
    for key in vars:
        print( key, vars[key], pulp.value( vars[key]) )

    solution = [ [] for pair in pairs ]
    for iPath in range(len(pairs)):
        for key in vars:
            if key[2] == iPath and pulp.value( vars[key]) > 0:
                solution[iPath].append( (key[0],key[1]) )

    return solution

def printSolution( solution, pairs ):
    for iPair in range(len(pairs)):
        orderly = [pairs[iPair][0]]
        while len(solution[iPair]):
            nextEdge = [ edge for edge in solution[iPair] if edge[0] == orderly[-1] ]
            nextEdge = nextEdge[0] # Will fail if the solution is broken
            iNext = solution[iPair].index(nextEdge)
            solution[iPair].pop( iNext )
            orderly.append( nextEdge[1] )
        print( f"Path {iPair}:")
        print( "->".join([str(v) for v in orderly]) )


def dijkstra( root, weights ):
    """Dijkstra's method for minimum distance of every vertex from a root vertex.
    
    Inputs:
    
    weights: dict of {edge: weight}, where edge is (tail,head)
    
    Outputs:
    dict of {vertex:distance}
    """
    distance = { root: 0 }
    parent = { root: None}
    reached = [ root ]
    done = False
    while not done:
        done = True
        frontier = {}
        for u, v in weights:
            if u not in reached: 
                continue
            if v not in reached:
                done = False
                if v not in frontier:
                    frontier[v] = distance[u] + weights[(u,v)]
                    parent[v] = u
                elif frontier[v] > distance[u] + weights[(u,v)]:
                    frontier[v] = distance[u] + weights[(u,v)]
                    parent[v] = u
        if not done:
            next = [v for v in frontier if frontier[v] == min(frontier.values())][0]
            reached.append( next )
            distance[next] = frontier[next]

    return distance, parent

def traceBack( destination, parent ):
    """Using Dijkstra's shortest-path parent links, trace back and find the shortest path."""
    path = [ destination ]
    while True:
        path.append( parent[path[-1]])
        if parent[path[-1]] is None:
            break
    path.reverse()
    return path
            
def suurb( root, destinations, edges ):
    """Suurballe's algorithm, after the 1984 rather than 1974 fashion.  Making
    this vertex-disjoint requires adding internal edges to all vertices."""

    startingWeights = { edge : 1 for edge in edges }
    startingDistances, sParents = dijkstra( root, startingWeights )

    firstPathVertices = traceBack( destinations[0], sParents )
    firstPathEdges = [ (u, v) for (u,v) in zip( firstPathVertices[:-1], firstPathVertices[1:]) ]

    # w'(u,v) = w(u,v) - d(s,v) + d(s,u)
    modDistances = { (u, v) : startingWeights[(u,v)] - startingDistances[v] + startingDistances[u]
                    for u, v in edges}
    
    residualWeights = {}
    for (u,v) in modDistances:
        if (u,v) not in firstPathEdges:
            residualWeights[(u,v)] = modDistances[(u,v)]
        else:
            # Edges on the first path are reversed and set to 0 weight.
            residualWeights[(v,u)] = 0

    residualDistances, residualParents = dijkstra( root, residualWeights )
    residualPathVertices = traceBack( destinations[1], residualParents )
    residualPathEdges = [ (u, v) for (u,v) in zip( residualPathVertices[:-1], residualPathVertices[1:]) ]

    # Now we need to find edges traversed in both directions.  These should be removed
    # from both paths, and instead used as "handoffs" between the two paths.
    # I think this should be doable by just redoing Dijkstra after giving those paths
    # a high weight.
    lastWeights = {}
    for (u,v) in firstPathEdges:
        if (v,u) not in residualPathEdges:
            lastWeights[(u,v)] = 0
        else:
            lastWeights[(u,v)] = 1
    for (u,v) in residualPathEdges:
        if (v,u) not in firstPathEdges:
            lastWeights[(u,v)] = 0
        else:
            lastWeights[(u,v)] = 1

    lastDistances, lastParents = dijkstra( root, lastWeights )
    finalFirstPath = traceBack( destinations[0], lastParents )
    finalSecondPath = traceBack( destinations[1], lastParents )
    return finalFirstPath, finalSecondPath


def diameter( edges ):
    """Dumb n^3 algorithm to find graph diameter."""
    diameter = 0
    fromVertices = set( [u for (u,v) in edges ] )
    for root in fromVertices:
        distance, _ = dijkstra( root, {(u,v):1 for (u,v) in edges})
        diameter = max( diameter, max( distance.values() ))
    return diameter

def approxSolveDp( pairs, edges ):
    """Approximation algorithm for disjoint-pairs, attempting to maximize the number
    of pairs connected with disjoint paths.  Presented as a user exercise in Williamson
    and Shmoys "The Design of Approximation Algorithms'."""

    diam = diameter( edges )
    sqrtArcs = math.floor(math.sqrt( len( edges ) ) )
    bound = min( diam, sqrtArcs )

    currEdges = list(edges )
    paths = []
    for pair in pairs:
        print( "Pair:", pair)
        distance, parent = dijkstra( pair[0], {(u,v):1 for (u,v) in currEdges})
        if distance[pair[1]] > bound:
            paths.append( None )
        else:
            path = traceBack( pair[1], parent )
            removeEdges = [(u,v) for (u,v) in zip( path[:-1], path[1:] ) ]
            paths.append( removeEdges )
            currEdges = [ edge for edge in currEdges if edge not in removeEdges ]
    
    for path in paths:
        print( path )
    
    count = sum( [ 1 for path in paths if path is not None ] )
    return paths, count



class DpGraph:
    """Container for edges of a graph, preventing duplicates."""
    def __init__(self, nPaths, digraph = True):
        self.edges = []
        self.nPaths = nPaths
        self.digraph = digraph

    def add_edges( self, edges ):
        for edge in edges:
            if edge not in self.edges:
                self.edges.append( edge )
            if not self.digraph:
                reversed = (edge[1], edge[0])
                if reversed not in self.edges:
                    self.edges.append( reversed )
    
    def __repr__( self ):
        return str( self.edges )