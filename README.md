# parcer_for_qmobi

Состоит из двух частей:<br>
main.py - отвечает за подъем локального сервера (по умолчанию 127.0.0.1, порт 8000)<br>
cgi-bin/exchange.py - конвертер валют из рублей в доллары и обратно, может сохранять результат в формате .json<br>
Запускается через main.py, окрывает дефолтный браузер и в нем вкладку с интерфейсом<br>
При падении выгружает ошибки в error.log и при возможности в интерфейс<br>
<br>
Написан на python 3.9<br>
Используются стандартные библиотеки python:<br>
http.server, webbrowser, datetime, cgi, cgitb, urllib.request, html, html.parser<br>
<br>
Проверен на mac os catalina + pycharm + chrome и windows 10 + pycharm + chrome
