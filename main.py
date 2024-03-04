from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
import requests
import socket
import json

#Вывод ошибок на экран (Статус)
def SetStatus(text, type):
    status_Label_m['text'] = 'Статус: ' + text
    status_Label['text'] = 'Статус: ' + text
    if type == 'Error':
        status_Label_m['fg'] = '#ff0000'
        status_Label['fg'] = '#ff0000'
    else:
        status_Label_m['fg'] = '#000000'
        status_Label['fg'] = '#000000'
        if text == '':
            status_Label_m['text'] = f'Статус: Соединено с {host}:{port}'
            status_Label['text'] = f'Статус: Соединено с {host}:{port}'

#region Прочие кнопки
#Обновление таблицы интерфейсов
def UpdateInterface():
    global server_interface
    server_interface = FillTableInterface()
    global server_models
    server_models = FillTableModels()

def ReloadInterfaces():
    try:
        resp = requests.put(f"http://{host}:{port}/ReloadInterfaces", timeout=TIMEOUT)
        if resp.text == 'Reloaded':
            UpdateInterface()
        else:
            SetStatus('Перезапустить интерфейсы не получилось', 'Error')
    except requests.ConnectionError as e:
        SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
    except Exception as e:
        SetStatus(str(e), 'Error')
#endregion

#region Обработка таблиц
#Сортировка столбцов таблицы моделей
def SortColumnModel(col, reverse):
    # получаем все значения столбцов в виде отдельного списка
    #(Числа)
    if col == 1 or col == 2:
        l = [(int(tree_m.set(k, col)), k) for k in tree_m.get_children("")]
    else:
        l = [(tree_m.set(k, col), k) for k in tree_m.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index, (_, k) in enumerate(l):
        tree_m.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    tree_m.heading(col, command=lambda: SortColumnModel(col, not reverse))

#Сортировка столбцов таблицы интерфейсов
def SortColumn(col, reverse):
    # получаем все значения столбцов в виде отдельного списка
    #(Числа)
    if col == 0:
        l = [(int(tree.set(k, col)), k) for k in tree.get_children("")]
    #(COM)
    #elif col == 1:
        #l = [(int(tree.set(k, col).split('COM')[1]), k) for k in tree.get_children("")]
    else:
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index, (_, k) in enumerate(l):
        tree.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    tree.heading(col, command=lambda: SortColumn(col, not reverse))

#Заполнение таблицы моделей значениями
def FillTableModels():
    tree_m.delete(*tree_m.get_children())
    global last_select_row_m
    last_select_row_m = ''
    m = list()
    models_drop['values'] = m
    try:
        resp = requests.get(f"http://{host}:{port}/Models", timeout=TIMEOUT)
        dict_models = eval(resp.text)
    except requests.ConnectionError as e:
        SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
        return dict()
    except Exception as e:
        SetStatus(str(e), 'Error')
        return dict()
    for key in dict_models.keys():
        l = list()
        m.append(key)
        l.append(key)
        l.append(dict_models[key]["baudrate"])
        l.append(dict_models[key]["bytesize"])
        l.append(dict_models[key]["timeout"])
        tree_m.insert("", END, values=l)
    models_drop['values'] = m
    SetStatus('','')
    return dict_models

#Заполнение таблицы интерфейсов значениями
def FillTableInterface():
    tree.delete(*tree.get_children())
    global last_select_row
    last_select_row = ''
    try:
        resp = requests.get(f"http://{host}:{port}/Interfaces", timeout=TIMEOUT)
        text = resp.text.split(';')
        dict_interface = eval(text[0])
        dict_numbers = eval(text[1])
    except requests.ConnectionError as e:
        SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
        return dict()
    except Exception as e:
        SetStatus(str(e), 'Error')
        return dict()

    for key in dict_interface.keys():
        l = list()
        l.append(key)
        l.append(dict_interface[key]["weightIP/COM"])
        l.append(dict_interface[key]["model"])
        l.append(dict_interface[key]["printerIP"])
        l.append(dict_interface[key]["data"])
        l.append(dict_interface[key]["time"])
        if key in dict_numbers:
            tag = ('use',)
        else:
            tag = ('usent',)
        tree.insert("", END, values=l, tags=tag)
        SetStatus('','')
    return dict_interface

#Заполнение полей из таблицы моделей по нажатию строки
def FillDataFromRowModel(event):
    try:
        rowid = tree_m.identify_row(event.y)
        if rowid != '':
            global last_select_row_m
            last_select_row_m = rowid
            name_entry.delete(0, END)
            name_entry.insert(0, tree_m.item(rowid)['values'][0])
            baudrate_drop.set(tree_m.item(rowid)['values'][1])
            bytesize_drop.set(tree_m.item(rowid)['values'][2])
            timeout_entry.delete(0, END)
            timeout_entry.insert(0, tree_m.item(rowid)['values'][3])
    except Exception as e:
        SetStatus(f'Ошибка при нажатии в пустое место таблицы или заголовок {e}', 'Error')

#Заполнение полей из таблицы интерфейсов по нажатию строки
def FillDataFromRow(event):
    try:
        rowid = tree.identify_row(event.y)
        if rowid != '':
            global last_select_row
            last_select_row = rowid
            number_entry.delete(0, END)
            number_entry.insert(0, tree.item(rowid)['values'][0])
            COMw_entry.delete(0, END)
            COMw_entry.insert(0, tree.item(rowid)['values'][1])
            models_drop.set(tree.item(rowid)['values'][2])
            IPp_entry.delete(0, END)
            IPp_entry.insert(0, tree.item(rowid)['values'][3])
            data_entry.delete(0, END)
            data_entry.insert(0, tree.item(rowid)['values'][4])
            time_entry.delete(0, END)
            time_entry.insert(0, tree.item(rowid)['values'][5])
    except Exception as e:
        SetStatus(f'Ошибка при нажатии в пустое место таблицы или заголовок {e}', 'Error')
#endregion

#region Интерфейсы
#Проверка на корректность вводимых данных в полях
def CheckInsertDataRow(l):
    # Проверка на корректность ввода даты
    def CheckData(s):
        if len(s) != 3:
            #print('Неверный формат даты')
            return False
        if len(s[2]) == 0:
            #print('Пустой год')
            return False
        for c in s[2]:
            if not c.isdigit():
                #print('Дата должна содержать только числа')
                return False
            if int(s[2]) == 0:
                #print('Неверно задан год')
                return False
        if len(s[1]) == 0:
            #print('Пустой месяц')
            return False
        for c in s[1]:
            if not c.isdigit():
                #print('Дата должна содержать только числа')
                return False
            if int(s[1]) == 0 or int(s[1]) > 12:
                #print('Неверно задан месяц')
                return False
        if len(s[0]) == 0:
            #print('Пустой день')
            return False
        for c in s[0]:
            if not c.isdigit():
                #print('Дата должна содержать только числа')
                return False
            y = int(s[2])
            m = int(s[1])
            d = int(s[0])
            v = False
            if y % 400 == 0:
                v = True
            elif y % 4 == 0 and y % 100 != 0:
                v = True
            if d == 0 or d > 31 or (d > 30 and (m == 4 or m == 6 or m == 9 or m == 11)) or (d > 29 and m == 2) or (
                    d > 28 and m == 2 and not v):
                #print('Неверно задан день')
                return False
        return True

    # Проверка на корректность ввода IP
    def CheckIP(s):
        if len(s) != 2:
            #print('Неверный формат данных')
            return False
        else:
            if len(s[1]) == 0 or len(s[1]) > 5:
                #print('Неправильная длина порта')
                return False
            for c in s[1]:
                if not c.isdigit():
                    #print('Неверно задан порт')
                    return False
            if int(s[1]) > 65535:
                #print('Порт не может превышать 65535')
                return False
            s = s[0].split('.')
            if len(s) != 4:
                #print('Неверно задан IP')
                return False
            for ss in s:
                if len(ss) == 0 or len(ss) > 4:
                    #print('Неправильная длина адреса')
                    return False
                for c in ss:
                    if not c.isdigit():
                        #print('Поле IP должно быть задано цифрами')
                        return False
                if int(ss) > 256:
                    #print('Адрес не может превышать 255')
                    return False
        return True

    q = True
    #number
    number_entry['bg'] = '#ffffff'
    if len(l[0]) == 0:
        #print('Поле не может быть пустым')
        number_entry['bg'] = '#ffe5e5'
        q = False
    else:
        for c in l[0]:
            if not c.isdigit():
                #print('Неверный формат')
                number_entry['bg'] = '#ffe5e5'
                q = False
                break
    #COM
    COMw_entry['bg'] = '#ffffff'
    if len(l[1]) == 0:
        #print('Поле не может быть пустым')
        COMw_entry['bg'] = '#ffe5e5'
        q = False
    else:
        if l[1].find('COM', 0) == -1:
            if not CheckIP(l[1].split(':')):
                COMw_entry['bg'] = '#ffe5e5'
                q = False
        elif l[1].find('COM', 0) != 0:
            #print('Неверный ввод COM-порта')
            COMw_entry['bg'] = '#ffe5e5'
            q = False
        else:
            s = l[1][3:]
            if len(s) == 0:
                #print('Нет номера порта')
                COMw_entry['bg'] = '#ffe5e5'
                q = False
            else:
                for c in s:
                    if not c.isdigit():
                        #print('В названии должны быть только цифры')
                        COMw_entry['bg'] = '#ffe5e5'
                        q = False
                        break
    #model
    if len(l[2]) == 0:
        q = False
    else:
        if not server_models.get(l[2], None):
            q = False
    #IPp
    IPp_entry['bg'] = '#ffffff'
    if len(l[3]) == 0:
        #print('Поле не может быть пустым')
        IPp_entry['bg'] = '#ffe5e5'
        q = False
    else:
        if not CheckIP(l[3].split(':')):
            IPp_entry['bg'] = '#ffe5e5'
            q = False
    #data
    data_entry['bg'] = '#ffffff'
    if len(l[4]) != 0:
        if not CheckData(l[4].split('.')):
            data_entry['bg'] = '#ffe5e5'
            q = False
    #time
    time_entry['bg'] = '#ffffff'
    if len(l[5]) != 0:
        s = l[5].split(':')
        if len(s) != 2:
            #print('Неверный формат времени')
            time_entry['bg'] = '#ffe5e5'
            return False
        if len(s[0]) == 0:
            #print('Неверно заданы часы')
            time_entry['bg'] = '#ffe5e5'
            return False
        else:
            for c in s[0]:
                if not c.isdigit():
                    #print('Дата должна содержать только числа')
                    time_entry['bg'] = '#ffe5e5'
                    return False
            if int(s[0]) > 23:
                #print('Неверно заданы часы')
                time_entry['bg'] = '#ffe5e5'
                return False
            if len(s[1]) == 0:
                #print('Неверно заданы минуты')
                time_entry['bg'] = '#ffe5e5'
                return False
            for c in s[1]:
                if not c.isdigit():
                    #print('Дата должна содержать только числа')
                    time_entry['bg'] = '#ffe5e5'
                    return False
                if int(s[1]) > 59:
                    #print('Неверно заданы минуты')
                    time_entry['bg'] = '#ffe5e5'
                    return False
    return q

#Добавление интерфейса
def AddRowToTable():
    UpdateInterface()
    number = number_entry.get()
    COM = COMw_entry.get()
    model = models_drop.get()
    IPp = IPp_entry.get()
    data = data_entry.get()
    time = time_entry.get()
    row_val = [number, COM, model, IPp, data, time]
    #Проверка на корректность вводимых данных
    if CheckInsertDataRow(row_val):
        #Проверка на существование такого же НОМЕРА ВЕСОВ
        if server_interface.get(number, None):
            showerror('Ошибка', 'Интерфейс с таким номером весов уже существует!\nНомер весов - УНИКАЛЬНОЕ число')
            return
        #Проверка на существование COMпорта с таким же номером
        for k in tree.get_children(''):
            if tree.item(k)['values'][1] == COM:
                showerror('Ошибка', 'Интерфейс с таким COMпортом уже существует!\nCOMпорт - УНИКАЛЕН')
                return
        #Проверка на соединение с сервером и успешное изменение данных
        i = {
            'weightIP/COM': COM,
            'model': model,
            'printerIP': IPp,
            'data': data,
            'time': time
        }
        text = {number : i}
        text = str(text)
        try:
            resp = requests.post(f"http://{host}:{port}/AddInterface", data=text, timeout=TIMEOUT)
            if resp.text == 'Error':
                SetStatus('Создать/Загрузить интерфейс не получилось', 'Error')
                return
            elif resp.text == 'Added':
                tag = ('use',)
            else:
                tag = ('usent',)
            tree.insert('', END, values=row_val, tags=tag)
            server_interface[number] = i
            SetStatus('','')
        except requests.ConnectionError as e:
            SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
        except Exception as e:
            SetStatus(str(e), 'Error')

#Изменение интерфейса
def ChangeRowFromData():
    if last_select_row == '':
        return
    number = number_entry.get()
    COM = COMw_entry.get()
    model = models_drop.get()
    IPp = IPp_entry.get()
    data = data_entry.get()
    time = time_entry.get()
    row_val = [number, COM, model, IPp, data, time]
    if CheckInsertDataRow(row_val):
        #Проверка на соответствие номера весов с заполненным полем номера весов
        if tree.item(last_select_row)['values'][0] != int(number):
            showerror('Ошибка','Неверно выбран номер весов для замены')
            return
        for k in tree.get_children(''):
            if k != last_select_row and tree.item(k)['values'][1] == COM:
                showerror('Ошибка', 'Интерфейс с таким COMпортом уже существует!\nCOMпорт - УНИКАЛЕН')
                return

        # Проверка на соединение с сервером и успешное изменение данных
        i = {
            'weightIP/COM': COM,
            'model': model,
            'printerIP': IPp,
            'data': data,
            'time': time
        }
        text = {number: i}
        text = str(text)
        try:
            resp = requests.put(f"http://{host}:{port}/ChangeInterface", data=text, timeout=TIMEOUT)
            if resp.text == 'Error':
                SetStatus('Изменить/Загрузить интерфейс не получилось', 'Error')
                return
            elif resp.text == 'Added':
                tag = ('use',)
            else:
                tag = ('usent',)
            tree.item(last_select_row, values=row_val, tags=tag)
            server_interface[number] = i
            SetStatus('','')
        except requests.ConnectionError as e:
            SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
        except Exception as e:
            SetStatus(str(e), 'Error')

#Удаление интерфейса
def DeleteRow():
    text = dict()
    if len(tree.selection()) == 0:
        return
    for selected_item in tree.selection():
        text[str(tree.item(selected_item)['values'][0])] = True
    text = str(text)
    try:
        resp = requests.delete(f"http://{host}:{port}/Interfaces", data=text, timeout=TIMEOUT)
        if resp.status_code == 400:
            SetStatus('Странная ошибка при удалении на сервере', 'Error')
        else:
            ans = eval(resp.text)
            err_text = list()
            #Проверка на соединение и удаление
            for selected_item in tree.selection():
                key = str(tree.item(selected_item)['values'][0])
                if key not in ans:
                    del server_interface[key]
                    tree.delete(selected_item)
                else:
                    err_text.append(key)
            SetStatus('','')
            if len(err_text) != 0:
                SetStatus(f'Весы: {err_text} не были удалены', 'Error')
    except requests.ConnectionError as e:
        SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
    except Exception as e:
        SetStatus(str(e), 'Error')
#endregion

#region Модели
#Проверка на корректность вводимых данных в полях
def CheckInsertDataRowModel(l):
    q = True
    #name
    name_entry['bg'] = '#ffffff'
    if len(l[0]) == 0:
        #print('Поле не должно быть пустым')
        name_entry['bg'] = '#ffe5e5'
        q = False
    #baudrate
    if len(l[1]) == 0:
        #print('Поле не должно быть пустым')
        q = False
    else:
        try:
            if not int(l[1]) in baudrates:
                #print('Поле не может принимать других значений, кроме заданных')
                q = False
        except Exception as e:
            #print(e)
            q = False
    #bytesize
    if len(l[2]) == 0:
        #print('Поле не должно быть пустым')
        q = False
    else:
        try:
            if not int(l[2]) in bytesizes:
                #print('Поле не может принимать других значений, кроме заданных')
                q = False
        except Exception as e:
            #print(e)
            q = False
    #timeout
    timeout_entry['bg'] = '#ffffff'
    if len(l[3]) == 0:
        #print('Поле не должно быть пустым')
        timeout_entry['bg'] = '#ffe5e5'
        return False
    else:
        for c in l[3]:
            if not c.isdigit():
                #print('Поле должно быть задано числом')
                timeout_entry['bg'] = '#ffe5e5'
                return False
    return q

#Добавление модели
def AddRowToTableModel():
    UpdateInterface()
    name = name_entry.get()
    baudrate = baudrate_drop.get()
    bytesize = bytesize_drop.get()
    timeout = timeout_entry.get()
    row_val = [name, baudrate, bytesize, timeout]
    #Проверка на кореектность вводимых данных
    if CheckInsertDataRowModel(row_val):
        #Проверка на уже существование такой модели
        if server_models.get(name, None):
            showerror('Ошибка', 'Модель с таким названием уже существует!\nНазвание модели - УНИКАЛЬНО')
            return
        # Проверка на соединение с сервером и успешное изменение данных
        m = {
            'baudrate': baudrate,
            'bytesize': bytesize,
            'timeout': timeout
        }
        text = {name: m}
        text = str(text)
        try:
            resp = requests.post(f"http://{host}:{port}/AddModel", data=text, timeout=TIMEOUT)
            if resp.text == 'Error' or resp.text == 'Not Added':
                SetStatus('Создать/Загрузить модель не получилось', 'Error')
                return
            tree_m.insert('', END, values=row_val)
            server_models[name] = m
            l = list(models_drop['values'])
            l.append(name)
            models_drop['values'] = l
            SetStatus('','')
        except requests.ConnectionError as e:
            SetStatus(f'Ошибка соединения к {host}:{port}', 'Error')
        except Exception as e:
            SetStatus(str(e), 'Error')

#Изменение модели
def ChangeRowFromDataModel():
    if last_select_row_m == '':
        return
    name = name_entry.get()
    baudrate = baudrate_drop.get()
    bytesize = bytesize_drop.get()
    timeout = timeout_entry.get()
    row_val = [name, baudrate, bytesize, timeout]
    if CheckInsertDataRowModel(row_val):
        #Проверка на соответствие номера весов с заполненным полем номера весов
        if tree_m.item(last_select_row_m)['values'][0] != name:
            showerror('Ошибка','Неверно выбрано название модели для замены')
            return
        # Проверка на соединение с сервером и успешное изменение данных
        m = {
            'baudrate': baudrate,
            'bytesize': bytesize,
            'timeout': timeout
        }
        text = {name: m}
        text = str(text)
        try:
            resp = requests.put(f"http://{host}:{port}/ChangeModel", data=text, timeout=TIMEOUT)
            tree_m.item(last_select_row_m, values=row_val)
            server_models[name] = m
            global server_interface
            server_interface = FillTableInterface()
            SetStatus('','')
            if resp.text == 'Error':
                SetStatus('Неопознанная ошибка. Изменить/Загрузить модель не получилось', 'Error')
            elif resp.text == 'Not Added':
                SetStatus('СОМпорт не запущен','Error')
        except requests.ConnectionError as e:
            SetStatus(f'Ошибка соединения с {host}:{port}', 'Error')
        except Exception as e:
            SetStatus(str(e), 'Error')

#Удаление модели
def DeleteRowModel():
    text = dict()
    if len(tree_m.selection()) == 0:
        return
    for selected_item in tree_m.selection():
        text[str(tree_m.item(selected_item)['values'][0])] = True
    text = str(text)
    try:
        resp = requests.delete(f"http://{host}:{port}/Models", data=text, timeout=TIMEOUT)
        if resp.status_code == 400:
            SetStatus('Странная ошибка при удалении на сервере', 'Error')
        else:
            ans = eval(resp.text)
            err_text = list()
            for selected_item in tree_m.selection():
                key = str(tree_m.item(selected_item)['values'][0])
                if key in ans:
                    del server_models[key]
                    tree_m.delete(selected_item)
                else:
                    err_text.append(key)
            UpdateInterface()
            if len(err_text) != 0:
                SetStatus(f'Модели: {err_text} не были удалены', 'Error')
    except requests.ConnectionError as e:
        SetStatus(f'Ошибка соединения к {host}:{port}', 'Error')
    except Exception as e:
        SetStatus(str(e), 'Error')
#endregion

if __name__ == '__main__':
    try:
        with open("config.json", 'r') as file:
            _config_params = json.load(file)
    except:
        with open("config.json", 'w') as file:
            _config_params = dict()
            _config_params['server'] = {'port': '8080', 'host': '192.168.9.156', 'timeout' : 0.2}
            json.dump(_config_params, file, indent=4)
    host = _config_params['server']['host']
    port = _config_params['server']['port']
    TIMEOUT = _config_params['server']['timeout']

    last_select_row = ''
    last_select_row_m = ''

    main_window = Tk()
    main_window.title("Управление интерфейсами")
    main_window.geometry("815x525+550+200")
    main_window.wm_minsize(815,525)
    main_window.rowconfigure(index=0, weight=1)
    main_window.columnconfigure(index=0, weight=1)

    tab_control = ttk.Notebook(main_window)
    tabInterface = ttk.Frame(tab_control)
    tabModel = ttk.Frame(tab_control)
    tab_control.add(tabInterface, text='Интерфейсы')
    tab_control.add(tabModel, text='Модели')
    tab_control.pack(expand=1, fill='both')


    status_Label = Label(tabInterface, text='Статус: ', anchor='w', font=("Arial", 10))
    status_Label.grid(row=1, column=0, sticky="nsew", padx=2)
    status_Label_m = Label(tabModel, text='Статус: ', anchor='w', font=("Arial", 10))
    status_Label_m.grid(row=1, column=0, sticky="nsew", padx=2)

    #Вкладка Интерефейсов
    tabInterface.rowconfigure(index=0, weight=1)
    tabInterface.columnconfigure(index=0, weight=1)

    interface_frame = LabelFrame(tabInterface, text='Список интерфейсов')
    interface_frame.grid(row=0, column=0, sticky="nsew", padx=2)
    in_interface_frame = Frame(interface_frame)
    in_interface_frame.grid(row=0, column=0, sticky="nsew")
    # определяем столбцы
    columns = ("Number", "weightCOM_IP", "model", "PrinterIP", "Data", "Time")
    tree = ttk.Treeview(in_interface_frame, columns=columns, show="headings")
    tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=2)
    # определяем заголовки
    tree.heading("Number", text="№", anchor=CENTER, command=lambda: SortColumn(0, False))
    tree.heading("weightCOM_IP", text="COM/IP Весов", anchor=CENTER, command=lambda: SortColumn(1, False))
    tree.heading("model", text="Модель", anchor=CENTER, command=lambda: SortColumn(2, False))
    tree.heading("PrinterIP", text="IP Принтера", anchor=CENTER, command=lambda: SortColumn(3, False))
    tree.heading("Data", text="Дата", anchor=CENTER, command=lambda: SortColumn(4, False))
    tree.heading("Time", text="Время", anchor=CENTER, command=lambda: SortColumn(5, False))
    tree.column("#1", stretch=YES, width=25, anchor=CENTER)
    tree.column("#2", stretch=YES, width=100, anchor=CENTER)
    tree.column("#3", stretch=YES, width=175, anchor=CENTER)
    tree.column("#4", stretch=YES, width=100, anchor=CENTER)
    tree.column("#5", stretch=YES, width=100, anchor=CENTER)
    tree.column("#6", stretch=YES, width=100, anchor=CENTER)
    tree.tag_configure('use', background='#e5fff6')
    tree.tag_configure('usent', background='#ffe5e5')
    # добавляем вертикальную прокрутку
    scrollbar = ttk.Scrollbar(in_interface_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")
    #Нажатие на строку таблицы
    tree.bind('<Button 1>', FillDataFromRow)

    server_interface = FillTableInterface()

    button_frame = LabelFrame(tabInterface, text='Управление')
    button_frame.grid(row=0, column=1, sticky="nsew", padx=2)
    btn_update = Button(button_frame, text="Обновить", command=UpdateInterface)
    btn_update.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    btn_reload = Button(button_frame, text="Перезапустить интерфейсы", command=ReloadInterfaces)
    btn_reload.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
    #Поле собственного IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    label = Label(tabInterface, text=f'Текущий IP: {s.getsockname()[0]}')
    s.close()
    label.grid(row=1, column=1, sticky="nsew", padx=5)

    change_interface_frame = LabelFrame(interface_frame, text='Добавление/Изменение/Удаление интерфейсов')
    change_interface_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    enter_interface_frame = Frame(change_interface_frame)
    enter_interface_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    number_Label = Label(enter_interface_frame, text='Номер весов:', anchor='w' ,font=("Arial bold", 10))
    number_Label.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    number_entry = Entry(enter_interface_frame, justify=CENTER, width=44)
    number_entry.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)
    COMw_Label = Label(enter_interface_frame, text='COM/IP весов:', anchor='w' ,font=("Arial", 10))
    COMw_Label.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
    COMw_entry = Entry(enter_interface_frame, justify=CENTER)
    COMw_entry.grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
    model_Label = Label(enter_interface_frame, text='Модель:', anchor='w' ,font=("Arial", 10))
    model_Label.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)

    IPp_Label = Label(enter_interface_frame, text='IP принтера:', anchor='w' ,font=("Arial", 10))
    IPp_Label.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
    IPp_entry = Entry(enter_interface_frame, justify=CENTER)
    IPp_entry.grid(row=3, column=1, sticky="nsew", padx=5, pady=2)
    data_Label = Label(enter_interface_frame, text='Дата(dd.mm.yy):', anchor='w' ,font=("Arial", 10), width=14)
    data_Label.grid(row=4, column=0, sticky="nsew", padx=5, pady=2)
    data_entry = Entry(enter_interface_frame, justify=CENTER)
    data_entry.grid(row=4, column=1, sticky="nsew", padx=5, pady=2)
    time_Label = Label(enter_interface_frame, text='Время(HH:MM):', anchor='w' ,font=("Arial", 10))
    time_Label.grid(row=5, column=0, sticky="nsew", padx=5, pady=2)
    time_entry = Entry(enter_interface_frame, justify=CENTER)
    time_entry.grid(row=5, column=1, sticky="nsew", padx=5, pady=2)

    button_frame2 = Frame(change_interface_frame)
    button_frame2.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
    button_Add = Button(button_frame2, text='Добавить интерфейс', command=AddRowToTable)
    button_Add.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    button_Change = Button(button_frame2, text='Изменить интерфейс', command=ChangeRowFromData)
    button_Change.grid(row=0, column=1, sticky="nsew", padx=7, pady=2)
    button_Delete = Button(button_frame2, text='Удалить интерфейс', command=DeleteRow)
    button_Delete.grid(row=0, column=2, sticky="nsew", padx=5, pady=2)

    #Вкладка Моделей
    tabModel.rowconfigure(index=0, weight=1)
    tabModel.columnconfigure(index=0, weight=1)

    model_frame = LabelFrame(tabModel, text='Список моделей')
    model_frame.grid(row=0, column=0, sticky="nsew", padx=2)
    in_model_frame = Frame(model_frame)
    in_model_frame.grid(row=0, column=0, sticky="nsew")
    #Определяем столбцы
    columns_m = ("Model", "baudrate", "bytesize", "timeout")
    tree_m = ttk.Treeview(in_model_frame, columns=columns_m, show="headings")
    tree_m.grid(row=0, column=0, sticky="nsew", padx=1, pady=2)
    #Определяем заголовки
    tree_m.heading("Model", text="Модель", anchor=CENTER, command=lambda: SortColumnModel(0, False))
    tree_m.heading("baudrate", text="baudrate", anchor=CENTER, command=lambda: SortColumnModel(1, False))
    tree_m.heading("bytesize", text="bytesize", anchor=CENTER, command=lambda: SortColumnModel(2, False))
    tree_m.heading("timeout", text="timeout", anchor=CENTER, command=lambda: SortColumnModel(3, False))
    tree_m.column("#1", stretch=YES, width=150, anchor=CENTER)
    tree_m.column("#2", stretch=YES, width=150, anchor=CENTER)
    tree_m.column("#3", stretch=YES, width=150, anchor=CENTER)
    tree_m.column("#4", stretch=YES, width=150, anchor=CENTER)
    #tree_m.tag_configure('use', background='#e5fff6')
    #tree_m.tag_configure('usent', background='#ffe5e5')
    #Добавляем вертикальную прокрутку
    scrollbar_m = ttk.Scrollbar(in_model_frame, orient=VERTICAL, command=tree_m.yview)
    tree_m.configure(yscroll=scrollbar_m.set)
    scrollbar_m.grid(row=0, column=1, sticky="ns")
    #Нажатие на строку таблицы
    tree_m.bind('<Button 1>', FillDataFromRowModel)

    models_drop = ttk.Combobox(enter_interface_frame, values=[], justify=CENTER, state="readonly")
    models_drop.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)
    server_models = FillTableModels()

    button_frame_m = LabelFrame(tabModel, text='Управление')
    button_frame_m.grid(row=0, column=1, sticky="nsew", padx=2)
    btn_m_update = Button(button_frame_m, text="Обновить", command=UpdateInterface, width=22)
    btn_m_update.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    #Поле собственного IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    label_m = Label(tabModel, text=f'Текущий IP: {s.getsockname()[0]}')
    s.close()
    label_m.grid(row=1, column=1, sticky="nsew", padx=5)

    change_model_frame = LabelFrame(model_frame, text='Добавление/Изменение/Удаление моделей')
    change_model_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    enter_model_frame = Frame(change_model_frame)
    enter_model_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    name_Label = Label(enter_model_frame, text='Название модели:', anchor='w', font=("Arial bold", 10))
    name_Label.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    name_entry = Entry(enter_model_frame, justify=CENTER, width=44)
    name_entry.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)
    baudrate_Label = Label(enter_model_frame, text='baudrate:', anchor='w', font=("Arial", 10))
    baudrate_Label.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
    baudrates = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 56000, 57600, 115200, 128000, 256000]
    baudrate_drop = ttk.Combobox(enter_model_frame, values=baudrates, justify=CENTER, state="readonly")
    baudrate_drop.grid(row=1, column=1, sticky="nsew", padx=5, pady=2)
    bytesize_Label = Label(enter_model_frame, text='bytesize:', anchor='w', font=("Arial", 10))
    bytesize_Label.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
    bytesizes = [4, 5, 6, 7, 8]
    bytesize_drop = ttk.Combobox(enter_model_frame, values=bytesizes, justify=CENTER, state="readonly")
    bytesize_drop.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)
    timeout_Label = Label(enter_model_frame, text='timeout:', anchor='w', font=("Arial", 10))
    timeout_Label.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
    timeout_entry = Entry(enter_model_frame, justify=CENTER)
    timeout_entry.grid(row=3, column=1, sticky="nsew", padx=5, pady=2)

    button_frame2_m = Frame(change_model_frame)
    button_frame2_m.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
    button_Add_m = Button(button_frame2_m, text='Добавить модель', width=16, command=AddRowToTableModel)
    button_Add_m.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
    button_Change_m = Button(button_frame2_m, text='Изменить модель', width=17, command=ChangeRowFromDataModel)
    button_Change_m.grid(row=0, column=1, sticky="nsew", padx=7, pady=2)
    button_Delete_m = Button(button_frame2_m, text='Удалить модель', width=16, command=DeleteRowModel)
    button_Delete_m.grid(row=0, column=2, sticky="nsew", padx=5, pady=2)

    main_window.mainloop()