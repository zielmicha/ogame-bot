#!/usr/bin/python
import ogame_api as api
import ogame_tool
import ogame_scenarios
import ogame_db
import sys
import time

def fun_oldbot():
    load_info()
    ogame_tool.do_things()

def fun_reload():
    ogame_db.write('cache_info', None)
    load_info()

def fun_do_scenario(name):
    load_info()
    ogame_tool.do_scenario(name)

def fun_show():
    load_info()
    print '-- buildings --'
    for a, b in Info.levels.items():
        print a, b
    print '-- resources --'
    for a, b in Info.resources.items():
        print a, b
    
def load_info():
    # this can be done prettier
    api.Info = ogame_db.load('cache_info')
    
    if not api.Info:
        api.load_info()
        ogame_db.write('cache_info', api.Info)
    
HELP = '\n'.join( '  --' + k[4:].replace('_', '-') for k in globals().keys() if k.startswith('fun_') ) + '\n  --help'

def main():
    args = sys.argv[1:]
    if len(args) < 1 or args[0][:2] != '--':
        print HELP
        sys.exit()
    fun_name = args[0][2:].replace('-', '_')
    try:
        method = globals()['fun_' + fun_name]
    except KeyError:
        print HELP
        sys.exit()
    method(*args[1:])
 


if __name__ == '__main__':
    main()
