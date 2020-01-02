#this is an example problem from the d'wave ocean docs that finds the minimum number of colors that are required to color each state such that no two states of the same color are touching;  it uses the dwave hybrid library
#run this code after running setup.py to make sure that the collected dwave packages work correctly
#see "https://docs.ocean.dwavesys.com/en/latest/examples/map_kerberos.html#map-kerberos" for information on the code
#I did not write this code, and I am not taking any credit for it
import networkx as nx

G = nx.read_adjlist('usa.adj', delimiter = ',')

import dwave_networkx as dnx
from hybrid.reference.kerberos import KerberosSampler

coloring = dnx.min_vertex_coloring(G, sampler=KerberosSampler(), chromatic_ub=4, max_iter=10, convergence=3)
print (set(coloring.values()))

'''import matplotlib.pyplot as plt
node_colors = [coloring.get(node) for node in G.nodes()]
if dnx.is_vertex_coloring(G, coloring):  # adjust the next line if using a different map
    nx.draw(G, pos=nx.shell_layout(G, nlist = [list(G.nodes)[x:x+10] for x in range(0, 50, 10)] + [[list(G.nodes)[50]]]), with_labels=True, node_color=node_colors, node_size=400, cmap=plt.cm.rainbow)
plt.show()'''#havn't gotten this to work on pi yet
