
from collections import namedtuple

ResTuple = namedtuple('ResTuple', 'crystal metal deuterium mult')

b_metal_mine = ResTuple(60, 15, 0, 1.5)
b_crystal_mine = ResTuple(48, 24, 0, 1.6)
b_deuterium_mine = ResTuple(225, 75, 0, 1.5)
b_power_plant = ResTuple(75, 30, 0, 1.5)

from browser_api import *

class InfoC:
    ' container for information (just not to use global varibles) '

    def __repr__(self):
        return repr(self.__dict__)

    def __getitem__(self, s):
        return getattr(self, s.replace('-', '_'))

    def items(self):
        return [ (k, getattr(self, k)) for k in dir(self) if not k.startswith('_') and not hasattr(InfoC, k) ]

Info = InfoC()

_has_logged = False
def ensure_login():
    global _has_logged
    if not _has_logged:
        api.login()
        _has_logged = True

def login():
    if not is_on_screen('in-game.png'):
        print 'logging in'
    
        set_url('http://ogame.pl')
        sleep(1)
        
        if not is_on_screen('close-login.png'):
            click_on('login.png', confidence = 0.97)
        else:
            print 'close login on screen'
        
        wait_for('login-do.png')
            
        eval_js('''document.getElementById('usernameLogin').value = 'zielmicha' ''')
        eval_js('''document.getElementById('passwordLogin').value = '1 packets transmitte' ''')
        eval_js('''document.getElementById('serverLogin').value = 'uni106.ogame.pl' ''')

        click_on('login-do.png')
        
        wait_for('in-game.png')
    else:
        print 'aleardy logged'

def load_info():
    global Info
    wait_for('in-game.png')

    ensure_on_screen('resources')

    Info = InfoC()
    
    print 'get resources'
    Info.resources = InfoC()
    Info.resources.metal = get_int('#resources_metal')
    Info.resources.crystal = get_int('#resources_crystal')
    Info.resources.deuterium = get_int('#resources_deuterium')
    Info.resources.energy = get_int('#resources_energy')

    print 'get levels'
    Info.levels = InfoC()
    Info.levels.metal_mine = get_level('#button1 .level')
    Info.levels.crystal_mine = get_level('#button2 .level')
    Info.levels.deuterium_mine = get_level('#button3 .level')
    Info.levels.power_plant = get_level('#button4 .level')

    print 'get can build'
    Info.can_build = InfoC()
    Info.can_build.metal_mine = is_on_screen('metal-mine.png')
    Info.can_build.crystal_mine = is_on_screen('crystal-mine.png')
    Info.can_build.deuterium_mine = is_on_screen('deuterium-mine.png')
    Info.can_build.power_plant = is_on_screen('power-plant.png')


def ensure_on_screen(name):
    if not is_on_screen(name + '-button.png'):
        click_on(name + '-button-inact.png')
        wait_for(name + '-button.png')
    
def get_level(selector):
    return int(get_text(selector).split()[-1])

def build_if_can(name, _force=False):
    if not _force and not Info.can_build[name]:
        print 'not attempting to build', name
        return
    
    ensure_login()
    
    ensure_on_screen('resources')

    if is_on_screen('improve.png', confidence = 0.95):
        # cycle back though preview
        print 'closing improve dialog'
        click_on('preview-button-inact.png')
        click_on('resources-button-inact.png')
    
    print 'building', name,
    if is_on_screen(name + '.png'):
        click_on(name + '.png')
        click_on('improve.png', confidence = 0.95)
        print 'ok'
        return True
    else:
        print 'not possible'
        return False

