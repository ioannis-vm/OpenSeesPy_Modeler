"""
Braced frame design model.

Length units: in
Force units: lb
"""

import numpy as np

from osmg.analysis.common import UDL
from osmg.analysis.load_case import LoadCaseRegistry
from osmg.analysis.recorders import NodeRecorder
from osmg.analysis.supports import FixedSupport
from osmg.core.model import Model2D
from osmg.creators.component import BeamColumnCreator
from osmg.creators.section import AISC_Database_Section_Creator
from osmg.graphics.plotly import (
    DeformationConfiguration,
    Figure3D,
    Figure3DConfiguration,
)
from osmg.model_objects.node import Node
from osmg.model_objects.section import ElasticSection

# Instantiate model object
frame = Model2D(name='Gridline B', dimensionality='2D Frame')

# Add grid lines
grids = frame.grid_system
grids.add_level('0', 0.00)
grids.add_level('1', 15.00 * 12.00)
grids.add_level('2', (15.00 + 13.00) * 12.00)
grids.add_level('3', (15.00 + 2.0 * 13.00) * 12.00)
grids.add_level('4', (15.00 + 3.0 * 13.00) * 12.00)
grids.add_grid('A', 0.00)
grids.add_grid('B', 25.00 * 12.00)
grids.add_grid('C', 25.00 * 2.0 * 12.00)
grids.add_grid('D', 25.00 * 3.0 * 12.00)
grids.add_grid('E', 25.00 * 4.0 * 12.00)
grids.add_grid('F', 25.00 * 5.0 * 12.00)

# Add primary nodes
for level in ('0', '1', '2', '3', '4'):
    for grid in ('A', 'B', 'C', 'D', 'E', 'F'):
        if (grid == 'A' and level == '4') or (grid == 'F' and level == '4'):
            continue
        frame.nodes.add(
            Node(
                uid_generator=frame.uid_generator,
                coordinates=(
                    grids.get_grid_location(grid),
                    grids.get_level_elevation(level),
                ),
            ),
        )

# Find the node at 'A'-'Base'
found_node = frame.nodes.search_by_coordinates_or_raise(
    (
        grids.get_grid_location('A'),
        grids.get_level_elevation('0'),
    )
)

# Define a common section
simple_section = ElasticSection(
    frame.uid_generator,
    'Test Section',
    e_mod=1e3,
    area=1e3,
    i_y=1.00,
    i_x=1.00,
    g_mod=1.00,
    j_mod=1.00,
    sec_w=0.00,
)

e_modulus = 29000000.00  # lb/in2
g_modulus = 11500000.00  # lb/in2

# Define an AISC W section
section_creator = AISC_Database_Section_Creator(frame.uid_generator)
column_section = section_creator.load_elastic_section(
    section_label='W14X120', e_modulus=1.00, g_modulus=1.00
)
beam_section = section_creator.load_elastic_section(
    section_label='W18X119', e_modulus=1.00, g_modulus=1.00
)

# Add columns
bcg = BeamColumnCreator(frame, 'elastic')
added_columns = []
for level in ('1', '2', '3', '4'):
    previous_level = str(int(level) - 1)
    for grid in ('A', 'B', 'C', 'D', 'E', 'F'):
        if level == '4' and (grid in {'A', 'F'}):
            continue
        col = bcg.generate_plain_component_assembly(
            tags={'column'},
            node_i=frame.nodes.search_by_coordinates_or_raise(
                (
                    grids.get_grid_location(grid),
                    grids.get_level_elevation(level),
                )
            ),
            node_j=frame.nodes.search_by_coordinates_or_raise(
                (
                    grids.get_grid_location(grid),
                    grids.get_level_elevation(previous_level),
                )
            ),
            n_sub=1,
            eo_i=np.array((0.00, 0.0)),
            eo_j=np.array((0.00, 0.0)),
            section=column_section,
            transf_type='Linear',
        )
        added_columns.append(col)

# Add beams
added_beams = []
for level in ('1', '2', '3', '4'):
    for grid_i, grid_j in zip(('A', 'B', 'C', 'D', 'E'), ('B', 'C', 'D', 'E', 'F')):
        if level == '4' and (grid_i == 'A' or grid_j == 'F'):
            continue
        beam = bcg.generate_plain_component_assembly(
            tags={'beam'},
            node_i=frame.nodes.search_by_coordinates_or_raise(
                (
                    grids.get_grid_location(grid_i),
                    grids.get_level_elevation(level),
                )
            ),
            node_j=frame.nodes.search_by_coordinates_or_raise(
                (
                    grids.get_grid_location(grid_j),
                    grids.get_level_elevation(level),
                )
            ),
            n_sub=1,
            eo_i=np.array((12.00, 12.0)),
            eo_j=np.array((12.00, 12.0)),
            section=column_section,
            transf_type='Linear',
        )
        added_beams.append(beam)


# Create a load case registry
load_case_registry = LoadCaseRegistry(frame)

# Create a load case and add fixed supports
fixed_support = FixedSupport((True, True, True))
load_case_registry.dead['D'].add_supports_at_level(frame, fixed_support, '0')

# Example of how to retrieve a primary node:
# Locate the nodes at 'A'-'Level 1' and 'B'-'Level 1'
frame.nodes.search_by_coordinates_or_raise(
    (grids.get_grid_location('A'), grids.get_level_elevation('0'))
)

# Add UDLs to the beams
for beam in added_beams:
    load_case_registry.dead['D'].load_registry.element_udl[beam.uid] = UDL(
        (0.0, -10.00)
    )  # lb/in

# load_case_registry.dead['B'].load_registry.element_udl[top_beam.uid] = UDL(
#     (0.0, +10.00)
# )  # lb/in

# # Add a concentrated point load at 'A'-'Level 1' in load case 'C'
# load_case_registry.dead['C'].load_registry.nodal_loads[node_a_level1.uid] = (
#     PointLoad(
#         (0.0, 10.00, 0.00)  # lb
#     )
# )

# Add an extra recorder
load_case_registry.dead['D'].analysis.recorders['node_envelope'] = NodeRecorder(
    uid_generator=frame.uid_generator,
    recorder_type='EnvelopeNode',
    nodes=(
        frame.nodes.search_by_coordinates_or_raise(
            (
                grids.get_grid_location('A'),
                grids.get_level_elevation('3'),
            )
        ).uid,
    ),
    dofs=(1, 2, 3),
    response_type='disp',
    file_name='envelope',
    output_time=True,
    number_of_significant_digits=6,
)

# Run analysis
load_case_registry.run()

result_dir = load_case_registry.dead['D'].analysis.settings.result_directory
print(f'Result directory: {result_dir}')  # noqa: T201

displ = load_case_registry.dead['D'].analysis.recorders['default_node'].get_data()
forces = (
    load_case_registry.dead['D']
    .analysis.recorders['default_beamcolumn_basic_forces']
    .get_data()
)


recorder = load_case_registry.dead['D'].analysis.recorders['default_node']
assert isinstance(recorder, NodeRecorder)
deformation_configuration = DeformationConfiguration(
    reference_length=frame.reference_length(),
    ndf=3,
    recorder=recorder,
    step=0,
    amplification_factor=None,  # Figure it out.
)


fig = Figure3D(Figure3DConfiguration(ndm=2))
fig.add_nodes(list(frame.nodes.values()), 'primary', overlay=True)
fig.add_nodes(list(frame.nodes.values()), 'primary', deformation_configuration)
fig.add_components(list(frame.components.values()), overlay=True)
fig.add_components(list(frame.components.values()), deformation_configuration)
fig.add_supports(
    frame.nodes, load_case_registry.dead['D'].fixed_supports, symbol_size=12.00
)
fig.add_udl(
    load_case_registry.dead['D'].load_registry.element_udl,
    frame.components,
    force_to_length_factor=5.00,
    offset=0.00,
)
fig.add_loads(
    load_case_registry.dead['D'].load_registry.nodal_loads,
    frame.nodes,
    force_to_length_factor=5.00,
    offset=0.0,
    head_length=12.0,
    head_width=12.0,
    base_width=3.0,
)
# fig.add_basic_forces(frame.components)
fig.show()

"""
TODO








# Remaining tasks
- [X] Finalize default recorders
- [X] Code to read back results from OpenSees: use recorder objects
  - [ ] Also try envelope recorders, drift recorder <<<<<<<<<<<<<<<
        (needs work. will come back later.)
- [ ] Plotting of displacements and basic forces
  - [ ] See if local system works correctly with offsets.
- [ ] Load Case Combinations
- [ ] Ability to utilize the "release" flag for elastic beamcolumn elements (?).
- [ ] Add back hinged component assembly
- [ ] Add back modal, pushover, time-history analysis.
- [ ] Work on code for steel design checks.

"""
print()  # noqa: T201