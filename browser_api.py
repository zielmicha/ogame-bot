import socket
import os
import cv2
import numpy

from time import sleep, time
import random
from random import randrange

sock = socket.socket(socket.AF_UNIX)
sock.connect('browser.sock')
sock_file = sock.makefile('r+', 1)

pattern_cache = {}
render_cache = None
render_cache_last = 0

def _call(*args):
    sock_file.write(' '.join(map(str, args)) + '\n')

def call_result(*args):
    _call(*args)
    return sock_file.readline().strip()

def call_noresult(*args):
    _call(*args)

def get_size():
    return map(int, call_result('get-size').split())

def set_url(url):
    call_noresult('set-url', url)

def eval_js(js):
    call_result('javascript', js.encode('base64').replace('\n', ''))

def click(x, y):
    call_noresult('click', x, y)

def get_text(selector):
    return call_result('get', selector).decode('base64')

def get_int(selector):
    t = get_text(selector)
    t = t.replace('.', '')
    return int(t)

def render(cache=True):
    global render_cache, render_cache_last
    if cache and (time() - render_cache_last) < 1.5:
        return render_cache
    
    path = call_result('render')
    render_cache = img = cv2.imread(path)
    render_cache_last = time()
    os.remove(path)
    return img

def find_pattern(img, pattern, confidence = 0.99):
    if isinstance(pattern, tuple):
        return sum([ find_pattern(img, i) for i in pattern ], [])
    
    if isinstance(pattern, basestring):
        if pattern not in pattern_cache:
            assert os.path.exists(pattern), '%s does not exist' % pattern # weird cv2 errors
            pattern_cache[pattern] = cv2.imread(pattern)
        pattern = pattern_cache[pattern]

    result = cv2.matchTemplate(img, pattern, cv2.TM_CCOEFF_NORMED)

    match_indices = numpy.arange(result.size)[(result>confidence).flatten()]

    coord = zip(*numpy.unravel_index(match_indices, result.shape))
    
    return [
        (x + pattern.shape[1]/2, y + pattern.shape[0]/2)
        for y, x in coord ]

wait_time = 4.0

def is_on_screen(pattern, **kwargs):
    return bool(find_pattern(render(), pattern, **kwargs))

def wait_for(pattern, **kwargs):
    DELTA = 0.3
    
    for i in xrange(int(wait_time / DELTA) + 1):
        found = find_pattern(render(cache=False), pattern, **kwargs)
        if found:
            return found[0]
        
        sleep(DELTA)
    raise TooLongError('waited too long for %s' % pattern)

class TooLongError(Exception):
    pass

def click_on(pattern, **kwargs):
    x, y = wait_for(pattern, **kwargs)
    click(x, y)

def random_sleep(min, max):
    sleep(randfloat(min, max))

def randfloat(min, max):
    return random.random() * (max - min) + min
