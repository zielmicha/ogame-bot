import pygame
import socket
import time
import os

sock = socket.socket(socket.AF_UNIX)
sock.connect('browser.sock')
sock_file = sock.makefile('r+', 1)

def _call(*args):
    sock_file.write(' '.join(map(str, args)) + '\n')

def call_result(*args):
    _call(*args)
    return sock_file.readline().strip()

def call_noresult(*args):
    _call(*args)

def get_size():
    return map(int, call_result('get-size').split())

ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19'

call_noresult('user-agent', ua)

size = get_size()

print 'window size', size

window = pygame.display.set_mode(size)

while True:
    events = pygame.event.get()

    for ev in events:
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                call_noresult('click', *ev.pos)
            else:
                print ev.pos
        elif ev.type == pygame.QUIT:
            break

    path = call_result('render')

    image = pygame.image.load(path)
    window.blit(image, (0, 0))
    os.remove(path)

    pygame.display.flip()
    
    time.sleep(0.2)
