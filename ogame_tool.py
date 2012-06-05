import ogame_api as api
import ogame_scenarios

from collections import namedtuple

ResTuple = namedtuple('ResTuple', 'crystal metal deuterium mult')

b_metal_mine = ResTuple(60, 15, 0, 1.5)
b_crystal_mine = ResTuple(48, 24, 0, 1.6)
b_deuterium_mine = ResTuple(225, 75, 0, 1.5)
b_power_plant = ResTuple(75, 30, 0, 1.5)

def do_things():
    # old bot

    Info = api.Info
    
    if Info.resources.energy < 0:
        api.build_if_can('power-plant')
        return
    
    norm_levels = [Info.levels.metal_mine, Info.levels.crystal_mine + 2, Info.levels.deuterium_mine * 1.5 + 4]
    to_build = norm_levels.index(min(norm_levels))
    if to_build == 0:
        api.build_if_can('metal-mine')
    elif to_build == 1:
        api.build_if_can('crystal-mine')
    elif to_build == 2:
        api.build_if_can('deuterium-mine')

def do_scenario(name):
    steps = load_scenario(name)

    Info = api.Info
    
    if Info.resources.energy < 0:
        print 'not enough energy - building power plant'
        api.build_if_can('power-plant')
        return False

    for name, desired_level in steps:
        if Info.levels[name] < desired_level:
            api.build_if_can(name)
            return False
    
    print 'scenario finished'
    return True
    
def load_scenario(name):
    descr = getattr(ogame_scenarios, name)
    steps = [ line.split(None, 1) for line in descr.splitlines() if line ]
    return [ (a, int(b)) for a, b in steps ]
