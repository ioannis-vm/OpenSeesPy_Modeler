"""
The following utility functions are used for data visualization
https://plotly.com/python/reference/
"""
#   __                 UC Berkeley
#   \ \/\   /\/\/\     John Vouvakis Manousakis
#    \ \ \ / /    \    Dimitrios Konstantinidis
# /\_/ /\ V / /\/\ \
# \___/  \_/\/    \/   April 2021
#
# https://github.com/ioannis-vm/OpenSeesPy_Building_Modeler/

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
from modeler import Building

# https://www.google.com/search?q=color+picker
GRID_COLOR = '#d1d1d1'
NODE_PRIMARY_COLOR = '#7ac4b7'
COLUMN_COLOR = '#0f24db'
BEAM_COLOR = '#0f24db'
FLOOR_COLOR = '#c4994f'
SUDL_COLOR = '#ab1a28'


def draw_level_geometry(building: Building, lvlname: str):
    """
    Shows the grids, beams, floor perimeters and UDLs
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')

    # retrieve the specified level
    level = building.levels.get(lvlname)

    # draw the gridlines
    for grd in building.gridsystem.grids:
        line = [
            grd.start,
            grd.end
        ]
        line_np = np.array(line)
        ax.plot(line_np[:, 0], line_np[:, 1], color=GRID_COLOR)

    # TODO draw the floor slabs and tributary areas
    # TODO draw floor center of mass

    # draw the beams
    for bm in level.beams.beam_list:
        line = [
            bm.node_i.coordinates[0:2],
            bm.node_j.coordinates[0:2]
        ]
        line_np = np.array(line)
        ax.plot(line_np[:, 0], line_np[:, 1], color=BEAM_COLOR)

    # draw the nodes
    points = []
    if level.nodes.node_list:
        for nd in level.nodes.node_list:
            points.append(nd.coordinates)
        points_np = np.array(points)
        ax.scatter(points_np[:, 0], points_np[:, 1], color=NODE_PRIMARY_COLOR)

    ax.margins(0.10)
    fig.show()