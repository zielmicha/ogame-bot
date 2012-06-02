
from collections import namedtuple

ResTuple = namedtuple('ResTuple', 'crystal metal deuterium mult')

b_metal_mine = ResTuple(60, 15, 0, 1.5)
b_crystal_mine = ResTuple(48, 24, 0, 1.6)
b_deuterium_mine = ResTuple(225, 75, 0, 1.5)
b_power_plant = ResTuple(75, 30, 0, 1.5)
