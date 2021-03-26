#!/usr/bin/env python3

import cgi
import cgitb
import urllib.request
import datetime
from html import escape
from html.parser import HTMLParser

URL = 'https://cbr.ru/'  # сайт центробанка, отсюда берется курс доллара
FILENAME = 'result'  # название файла, в который выводится результат операции

cgitb.enable()  # дебаггер для CGI, на случай, если что-то там упадёт

#  словарь с предполагаемыми ошибками
error_dict = {
    '00': 'Unidentified global error',  # что-то где-то упало, но не ясно что и где
    '10': 'Function \"get_usd_from_cbr error\"',  # ошибка в парсере
    '11': f'Cannot connect to {URL}',  # ошибка в парсере, не может подключится к сайту
    '12': f'Cannot find USD in {URL}',  # ошибка в парсере, не может найти доллары по ссылке
    '13': 'Cannot use found USD price',  # ошибка в парсере, доллары нашел, но не может достать
    '20': 'Function \"json_maker error\"',  # ошибка в модуле сохранения json
    '21': f'Cannot create {FILENAME}.json',  # ошибка в модуле сохранения json, не может создать файл
    '22': f'Cannot write to {FILENAME}.json',  # ошибка в модуле сохранения json, не может редактировать файл
    '30': 'Cannot generate page',  # не может вызвать страницу
    '31': 'No form on page',  # не может создать форму
    '32': 'Cannot take data from page form'  # не может извлечь данные из формы
}

error_message = []  # список ошибок


def some_error(error_number, ex):
    """
    Функция логирования ошибок
    Вызывается из except, принимает ожидаемый error_number (список в словаре error_dict выше) и exception в ex
    Ничего не возвращает, но записывает полученные ошибки в список error_message
    :param error_number: string
    :param ex: string
    """
    error_number = str(error_number)  # на случай, если ошибка пришла числом, а не строкой
    error_type = error_dict[error_number]  # извлекает из словаря тип ошибки
    now = str(datetime.datetime.now())  # время, когда произошла ошибка
    error_message.append(f'{now} || {error_number} || {error_type} || {ex} \n')  # добавляет ошибку в список ошибок
    log = open('error.log', 'a')  # создает/открывает файл лога ошибок
    log.write(message)  # записывает ошибки в лог ошибок


def get_usd_from_cbr(url):
    """
    Парсер
    Кастомизирован под сайт центробанка (cbr.ru)
    Заносит данные с сайта в список,
    находит в списке USD,
    находит в окрестностях USD цену на них (здесь и происходит кастомизация под конкретный сайт)
    Возвращает цену USD в типе float
    :param url: string
    :return usd_rub: float
    """
    try:
        with urllib.request.urlopen(url) as resp:  # открываю страницу, которую парсим
            page = str(resp.read())
    except Exception as exc:
        some_error('11', exc)

    page_d = []  # переменная списка для парсера

    class Parser(HTMLParser):  # парсер из доков HTMLParser, тэги не нужны, поэтому метод один - handle data
        def handle_data(self, data):
            page_d.append(data)

    parser = Parser()  # переменная класса парсер
    parser.feed(page)  # скармливаем страницу переменной

    try:
        dollar_index = page_d.index('USD')  # ищу доллары
    except Exception as exc:
        some_error('12', exc)
    try:
        usd_rub = float(page_d[dollar_index + 2].split(' ')[0].replace(',', '.'))  # делаю из строки доллара число
    except Exception as exc:
        some_error('13', exc)
    return usd_rub


def json_maker(filename, data):
    """
    Сохраняет словарь в json
    Принимает имя файла filename и словарь data
    Создаёт файл и сохраняет в него словарь
    NB Есть стандартная библиотека json, но тут всего одна задача
    :param filename: string
    :param data: dictionary
    """
    j_data = str(data)  # превращает словарь в строку
    j_data = j_data.replace('\'', '\"')  # заменяем ' на " как того требует формат json
    try:
        file = open(f'{filename}.json', 'w+')  # создаем (или открываем) файл для перезаписи
    except Exception as exc:
        some_error('21', exc)
    try:
        file.write(j_data)  # записывает джейсонифицированную строку в файл
    except Exception as exc:
        some_error('22', exc)


try:
    usd_price = get_usd_from_cbr(URL)  # получаем курс доллара для страницы
except Exception as exc:
    some_error('10', exc)

# генерируем страницу, проставляя в скриптах и табличке актуальный курс доллара

try:
    try:  # генерируем HTML страницу со скриптами и табличкой
        print('''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
        <script type="text/javascript">
        
        function convert_r_d()
        {
        ''',
              f'''
        y = {usd_price};
        ''',
        '''
        x = document.getElementById("rub").value;
        if(x == "")
        {document.getElementById("usd").value = "";}
        else
        {{z = x / y; document.getElementById("usd").value = z.toFixed(2);}}
        }
        
        function convert_d_r()
        {
        ''',
        f'''
        y = {usd_price};
        ''',
        '''
        x = document.getElementById("usd").value;
        if(x == "")
        {document.getElementById("rub").value = "";}
        else
        {{z = x * y; document.getElementById("rub").value = z.toFixed(2);}}
        }
        </script>
            <form method="get" action="/cgi-bin/exchange.py">
                <table border="1">
                    <tr align="center">
                        <td width="200" height="15">
                            <p>Курс USD/RUB ЦБ РФ</p>
                        </td>
                        <td width="140">
                            <p>Рубли</p>
                        </td>
                        <td width="140">
                            <p>Доллары</p>
                        </td>
                    </tr>
                    <tr>
                        <td height="25">''',
              f'''{usd_price}''',
              '''
                        </td>
                        <td>
                            <input 
                                id="rub"
                                name="rub" 
                                type="number" 
                                placeholder="Введите сумму" 
                                step="0.01" 
                                min="0" 
                                max="999999999999999.99" 
                                oninput="convert_r_d()">
                        </td>
                        <td>
                            <input 
                                id="usd" 
                                name="usd" 
                                type="number" 
                                placeholder="Введите сумму" 
                                step="0.01" 
                                min="0" 
                                max="999999999999999.99" 
                                oninput="convert_d_r()">
                        </td>
                    </tr>
                    <tr>
                        <td height="30" colspan="3" align="center">
                            <button 
                                type="submit" 
                                value="submit" 
                                style="width: 300px; 
                                height: 25px">
                            Скачать результат в формате .json
                            </button>
                        </td>
                    </tr>
                </table>
            </form>
        </body>
        </html>
        ''')
    except Exception as exc:
        some_error('30', exc)

    try:
        form = cgi.FieldStorage()  # получаю данные из формы..
        usd = form.getfirst('usd', '0')  # ..рубли, если форма пустая - 0
        rub = form.getfirst('rub', '0')  # ..доллары, если форма пустая - 0
        usd = escape(usd)
        rub = escape(rub)
    except Exception as exc:
        some_error('31', exc)

    try:
        if usd <= '0' and rub <= '0':  # если форма пустая или каким-то образом меньше нуля - ничего не происходит
            pass
        else:
            # в ином случае результат передаётся в словарь result, запускется функция json_maker чтобы создать файл
            # и на странице вызывается скрипт скачивания этого файла
            result = {'RUB': float(rub), 'USD/RUB': usd_price, 'USD': float(usd)}
            try:
                json_maker(FILENAME, result)
                print('''
                <script>
        
                var link = document.createElement("a");
                link.download = "../result.json";
                link.target = "blank";
                link.href = "../result.json";
                document.body.appendChild(link);
                link.click();
        
                </script>
                ''')
            except Exception as exc:
                some_error('20', exc)
    except Exception as exc:
        some_error('32', exc)
except Exception as exc:
    some_error('00', exc)

# если возникает ошибка - выводим данные по ней/ним
if error_message:
    print(
        '''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Error</title>
        </head>
        <body>
        <p>
        An error has occurred!
        </p>
        '''
    )
    for message in error_message:
        message = escape(message)  # удаляет лишние для html символы из сообщения об ошибке
        print(f'''  # выводит ошибку в браузер
        <p>
            {message}
        </p>
        ''')
    print(
        '''
        </body>
        </html>
        '''
    )
