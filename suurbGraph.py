#! /usr/bin/env python

import random

random.seed(1000)

import project
import warnings

pairs = [ ( 0, 2 ), ( 1, 3 ) ]

edges = [ 
    ('s', 0),
    ('s', 1),
    (0,4),
    (4,5),
    (5,2),
    (1,4),
    (5,3),
    (1,6),
    (6,7),
    (7,8),
    (8,3)
]

g = project.DpGraph( 2 )
g.add_edges( edges )

solution = project.lpSolveDp( pairs, g.edges )

firstPath, secondPath = project.suurb( 's', [2,3], g.edges )
# Trim source 's' from front end
paths = [ firstPath[1:], secondPath[1:] ]
trimEdges = [ (u,v) for (u,v) in edges if u != 's' ]

distances, parents = project.dijkstra( 0, {edge:1 for edge in g.edges} )

print( "First path: ", firstPath )
print( "Second path:", secondPath)

try:
    import pygraphviz as pgv
    G = pgv.AGraph( directed=True )
    G.add_edges_from( trimEdges )
    
    G.subgraph( [ 0, 1 ], rank="source" )
    G.subgraph( [ 2, 3 ], rank="sink")

    with warnings.catch_warnings():
        warnings.filterwarnings( "ignore", message=".*3n.1 points" )
        G.layout( prog='dot', args = '-Grankdir=LR')

        colors = ['red', 'blue']
        for iPair in range(len(pairs)):
            orderly = [pairs[iPair][0]]
            while len(solution[iPair]):
                nextEdge = [ edge for edge in solution[iPair] if edge[0] == orderly[-1] ]
                nextEdge = nextEdge[0] # Will fail if the solution is broken
                G.get_edge(*nextEdge).attr["color"] = colors[iPair]
                iNext = solution[iPair].index(nextEdge)
                solution[iPair].pop( iNext )
                orderly.append( nextEdge[1] )
            print( f"Path {iPair}:")
            print( "->".join([str(v) for v in orderly]) )


        G.draw( f"suurbGraph.png" )

except Exception as e:
    print( f"Failed to draw display graph.")
    raise e
