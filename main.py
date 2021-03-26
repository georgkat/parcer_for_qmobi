#  qmobi currency converter and html parcer
#  no external library dependencies

import http.server
import webbrowser

# поднимаю локальный сервер

HandlerClass = http.server.SimpleHTTPRequestHandler
ServerClass = http.server.HTTPServer
Protocol = 'HTTP/1.0'
server_address = ('127.0.0.1', 8000)  # IP: 127.0.0.1, PORT: 8000
HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, http.server.CGIHTTPRequestHandler)

sa = httpd.socket.getsockname()

print('IP:', sa[0], 'PORT:', sa[1])
script = 'http://' + str(sa[0]) + ':' + str(sa[1]) + '/cgi-bin/exchange.py'  # формирую ссылку на скрипт обменника

webbrowser.open_new_tab(script)  # запускаю скрипт в браузере
httpd.serve_forever()  # оставляю сервер работать
