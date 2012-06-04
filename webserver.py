from PyQt4 import Qt, QtWebKit
import tempfile
import socket
import threading
import Queue
import os
from time import time

def main():
    view = QtWebKit.QWebPage()
    view.setViewportSize(Qt.QSize(1000, 800))
    view.mainFrame().load(Qt.QUrl('http://google.com'))
    
    def loaded():
        #for i in xrange(5):
        #    for j in xrange(5):
        #        click(5*i,5*j)
        click(10,10)
        
        print 'loaded'
        print 'end', image_temp.name

    request_queue = Queue.Queue(0)

    def server():
        sock = socket.socket(socket.AF_UNIX)
        sock_name = 'browser.sock'
        try:
            os.remove(sock_name)
        except OSError:
            pass

        sock.bind(sock_name)
        sock.listen(1)

        while True:
            client, addr = sock.accept()
            conn = client.makefile('r+', 1)
            print 'incoming connection', addr
            threading.Thread(target=connection_handler, args=[conn]).start()
            del addr, client, conn
        

    # actually it should be in connection_handler, but it causes segfaults
    img = Qt.QImage(view.viewportSize(), Qt.QImage.Format_ARGB32)
    painter = Qt.QPainter(img)
            
    def connection_handler(conn):

        def cmd_render():
            image_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            view.mainFrame().render(painter)
            img.save(image_temp.name)
            return image_temp.name

        def cmd_click(x, y):
            ev = Qt.QMouseEvent(Qt.QEvent.MouseButtonPress, Qt.QPoint(x, y), Qt.Qt.LeftButton, Qt.Qt.LeftButton, Qt.Qt.NoModifier)
            view.event(ev)
            ev = Qt.QMouseEvent(Qt.QEvent.MouseButtonRelease, Qt.QPoint(x, y), Qt.Qt.LeftButton, Qt.Qt.LeftButton, Qt.Qt.NoModifier)
            view.event(ev)

        def cmd_text(text):
            def do_key(key, letter):
                ev = Qt.QKeyEvent(Qt.QEvent.MouseButtonPress, key, Qt.Qt.NoModifier, letter)
                view.event(ev)
                ev = Qt.QKeyEvent(Qt.QEvent.MouseButtonRelease, key, Qt.Qt.NoModifier, letter)
                view.event(ev)
            
            for char in text:
                if char.upper() in 'ABCDEFGHIJKLMNOPQRSTUWXYZ':
                    k = getattr(Qt.Qt, 'Key_' + char.upper())
                    print k, char.upper()
                    do_key(k, char.upper())

        def cmd_js(code):
            return view.mainFrame().evaluateJavaScript(code)

        def cmd_url(url):
            view.mainFrame().load(Qt.QUrl(url))

        def cmd_get(selector):
            return unicode(view.mainFrame().findFirstElement(selector).toPlainText()).encode('utf8')
            
        while True:
            line = conn.readline().strip()
            if not line: break
            cmd, args = line.split(' ', 1) if ' ' in line else (line, '')
            if cmd == 'render':
                path = exec_in_ui(cmd_render)
                conn.write('%s\n' % path)
            elif cmd == 'get-size':
                size = view.viewportSize()
                conn.write('%d %d\n' % (size.width(), size.height()))
            elif cmd == 'text':
                exec_in_ui(cmd_text, args.decode('base64'))
            elif cmd == 'javascript':
                result = exec_in_ui(cmd_js, args.decode('base64'))
                conn.write('%s\n' % (str(result).encode('base64').replace('\n', '')))
            elif cmd == 'get':
                result = exec_in_ui(cmd_get, args)
                conn.write('%s\n' % result.encode('base64').replace('\n', ''))
            elif cmd == 'user-agent':
                pass # no way
            elif cmd == 'set-url':
                exec_in_ui(cmd_url, args)
            elif cmd == 'click':
                x, y = map(int, args.split())
                exec_in_ui(cmd_click, x, y)
            else:
                print 'unknown method', cmd

    last_request = [time()]
    def ui_op_handler():
        anything = False
        while True:
            try:
                callback = request_queue.get_nowait()
            except Queue.Empty:
                break

            callback()
            anything = True

        def setInterval(val):
            if val == timer.interval(): return 
            if val > timer.interval():
                print 'slowing down',
            elif val < timer.interval():
                print 'speeding up',
            print 'clock to %.1fHz' % (1000. / val)
            timer.setInterval(val)
            
        if anything:
            setInterval(max(timer.interval() / 8, 5))
            last_request[0] = time()
        elif time() - last_request[0] > 2:
            setInterval(min(timer.interval() * 8, 3000))

    def exec_in_ui(func, *args, **kwargs):
        response_queue = Queue.Queue(1)
        def wrapper_func():
            result = func(*args, **kwargs)
            response_queue.put(result)
        request_queue.put(wrapper_func)
        return response_queue.get()
    
    timer = Qt.QTimer(app)
    timer.timeout.connect(ui_op_handler)
    timer.start(1000)

    threading.Thread(target=server).start()
    

if __name__ == '__main__':
    app = Qt.QApplication([])
    app.setApplicationName("Chrome")
    app.setApplicationVersion("18.0.1025.151")
    
    main()
    
    app.exec_()


