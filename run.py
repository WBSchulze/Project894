#! /usr/bin/env python

import project
import random
import pulp

random.seed( 1000 )

# Graph 1.
# pairs = [ ( 0, 2 ), ( 1, 3 ) ]
# otherVertices = list( range( 4, 10 ) )
# g = project.DpGraph( 2 )
# g.add_edges( project.randomDisjointPaths( pairs, otherVertices ) )
# g.add_edges( project.randomSpanningTree( otherVertices ) )

# print(len(g.edges))

# # Graph 2.
# pairs = [ ( 0, 2 ), ( 1, 3 ) ]
# otherVertices = list( range( 4, 100 ) )
# g = project.DpGraph( 2 )
# g.add_edges( project.randomDisjointPaths( pairs, otherVertices ) )
# g.add_edges( project.randomSpanningTree( otherVertices ) )
# g.add_edges( project.randomSpanningTree( otherVertices ) )

# print(len(g.edges))

# # Graph 3.
# pairs = [ ( 0, 2 ), ( 1, 3 ) ]
# otherVertices = list( range( 4, 1000 ) )
# g = project.DpGraph( 2 )
# g.add_edges( project.randomDisjointPaths( pairs, otherVertices ) )
# g.add_edges( project.randomSpanningTree( otherVertices ) )
# g.add_edges( project.randomSpanningTree( otherVertices ) )

# print(len(g.edges))

# # Graph 4.
pairs = [ ( 0, 2 ), ( 1, 3 ) ]
otherVertices = list( range( 4, 10000 ) )
g = project.DpGraph( 2 )
g.add_edges( project.randomDisjointPaths( pairs, otherVertices ) )
g.add_edges( project.randomSpanningTree( otherVertices ) )
g.add_edges( project.randomSpanningTree( otherVertices ) )

print(len(g.edges))

solution = project.lpSolveDp( pairs, g.edges )
project.printSolution( solution, pairs )

