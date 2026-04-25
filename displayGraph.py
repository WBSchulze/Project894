#! /usr/bin/env python

import random

random.seed(1000)

import project
import warnings

nRows = 5
nColumns = 5

pairs = [ (u * nColumns, (u + 1) * nColumns - 1) for u in range( nRows ) ]

# 5 rows of intermediate vertices, 5 vertices long.
rows = []
for iRow in range( nRows ):
    rows.append( list( range( iRow * nColumns, (iRow + 1 ) * nColumns)))

rowEdges = []
# Add edges for each row.
for row in rows:
    for tail, head in zip( row[:-1], row[1:] ):
        rowEdges.append( (tail, head) )
        print( rowEdges[-1])
        if random.random() < 0.5:
            rowEdges.append( ( head, tail) )
            print( rowEdges[-1])

moreEdges = []
# Add edges between each pair of rows.
for highRow, lowRow in zip( rows[:-1], rows[1:] ):

    highChoices = sorted( random.choices( highRow[1:-1], k=3 ) )
    lowChoices = sorted( random.choices( lowRow[1:-1], k=3 ) )
    # print( highChoices, lowChoices )
    for high, low in zip( highChoices, lowChoices ):
        if random.random() < 0.5:
            moreEdges.append( (high, low) )
            # print( moreEdges[-1])
        if random.random() < 0.5:
            moreEdges.append( (low, high) )
            # print( moreEdges[-1])
        

g = project.DpGraph( nRows )
edges = rowEdges + moreEdges
g.add_edges( edges )

solution = project.lpSolveDp( pairs, g.edges )

try:
    import pygraphviz as pgv
    G = pgv.AGraph( directed=True )
    G.add_edges_from( edges )
    
    G.subgraph( [ u for (u,v) in pairs ], rank="source" )
    G.subgraph( [ v for (u,v) in pairs ], rank="sink")
    for iColumn in range(1,nColumns-1):
        G.subgraph( list(range(iColumn, nRows*nColumns, nRows)),rank="same")

    with warnings.catch_warnings():
        warnings.filterwarnings( "ignore", message=".*3n.1 points" )
        G.layout( prog='dot', args = '-Grankdir=LR')

        colors = ['red', 'blue', 'green', 'orange', 'purple' ]
        for iPair in range(len(pairs)):
            orderly = [pairs[iPair][0]]
            while len(solution[iPair]):
                print( "iPair", iPair, "Solution", solution[iPair])
                nextEdge = [ edge for edge in solution[iPair] if edge[0] == orderly[-1] ]
                nextEdge = nextEdge[0] # Will fail if the solution is broken
                G.get_edge(*nextEdge).attr["color"] = colors[iPair]
                iNext = solution[iPair].index(nextEdge)
                solution[iPair].pop( iNext )
                orderly.append( nextEdge[1] )
            print( f"Path {iPair}:")
            print( "->".join([str(v) for v in orderly]) )


        G.draw( f"ilpGraph.png" )

except Exception as e:
    print( f"Failed to draw display graph.")
    raise e
