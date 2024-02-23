from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
import requests
import socket
import json

#region Прочие кнопки
#Обновление таблицы интерфейсов
def UpdateInterface():
    global server_interface
    server_interface = FillTableInterface()

def ReloadInterfaces():
    try:
        resp = requests.put(f"http://{host}:{port}/ReloadInterfaces")
        if resp.text == 'Reloaded':
            UpdateInterface()
        else:
            print('Перезапустить интерфейсы не получилось')
    except requests.ConnectionError as e:
        print(f'Ошибка соединения к {host}:{port}')
    except Exception as e:
        print(e)
#endregion

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

#Заполнение таблицы значениями
def FillTableInterface():
    tree.delete(*tree.get_children())
    try:
        resp = requests.get(f"http://{host}:{port}/Interfaces")
        text = resp.text.split(';')
        dict_interface = eval(text[0])
        dict_numbers = eval(text[1])
    except requests.ConnectionError as e:
        print(f'Ошибка соединения к {host}:{port}')
        return dict()
    except Exception as e:
        print(e)
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
    return dict_interface

#Проверка на корректность данных в полях
def CheckInsertDataRow(l):
    # Проверка на корректность ввода даты
    def CheckData(s):
        if len(s) != 3:
            print('Неверный формат даты')
            return False
        if len(s[2]) == 0:
            print('Пустой год')
            return False
        for c in s[2]:
            if not c.isdigit():
                print('Дата должна содержать только числа')
                return False
            if int(s[2]) == 0:
                print('Неверно задан год')
                return False
        if len(s[1]) == 0:
            print('Пустой месяц')
            return False
        for c in s[1]:
            if not c.isdigit():
                print('Дата должна содержать только числа')
                return False
            if int(s[1]) == 0 or int(s[1]) > 12:
                print('Неверно задан месяц')
                return False
        if len(s[0]) == 0:
            print('Пустой день')
            return False
        for c in s[0]:
            if not c.isdigit():
                print('Дата должна содержать только числа')
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
                print('Неверно задан день')
                return False
        return True

    # Проверка на корректность ввода IP
    def CheckIP(s):
        if len(s) != 2:
            print('Неверный формат данных')
            return False
        else:
            if len(s[1]) == 0 or len(s[1]) > 5:
                print('Неправильная длина порта')
                return False
            for c in s[1]:
                if not c.isdigit():
                    print('Неверно задан порт')
                    return False
            if int(s[1]) > 65535:
                print('Порт не может превышать 65535')
                return False
            s = s[0].split('.')
            if len(s) != 4:
                print('Неверно задан IP')
                return False
            for ss in s:
                if len(ss) == 0 or len(ss) > 4:
                    print('Неправильная длина адреса')
                    return False
                for c in ss:
                    if not c.isdigit():
                        print('Поле IP должно быть задано цифрами')
                        return False
                if int(ss) > 256:
                    print('Адрес не может превышать 255')
                    return False
        return True

    #number
    if len(l[0]) == 0:
        print('Поле не может быть пустым')
        return False
    for c in l[0]:
        if not c.isdigit():
            print('Неверный формат')
            return False
    #COM
    if len(l[1]) == 0:
        print('Поле не может быть пустым')
        return False
    if l[1].find('COM', 0) == -1:
        if not CheckIP(l[1].split(':')):
            return False
    elif l[1].find('COM', 0) != 0:
        print('Неверный ввод COM-порта')
        return False
    else:
        s = l[1][3:]
        if len(s) == 0:
            print('Нет номера порта')
            return False
        for c in s:
            if not c.isdigit():
                print('В названии должны быть только цифры')
                return False
    #model
    if len(l[2]) == 0:
        print('Поле не может быть пустым')
        return False
    if not server_models.get(l[2], None):
        print('Такой модели нет в конфигурации')
        return False
    #IPp
    if len(l[3]) == 0:
        print('Поле не может быть пустым')
        return False
    if not CheckIP(l[3].split(':')):
        return False
    #data
    if len(l[4]) != 0:
        if not CheckData(l[4].split('.')):
            return False
    #time
    if len(l[5]) != 0:
        s = l[5].split(':')
        if len(s) != 2:
            print('Неверный формат времени')
            return False
        if len(s[0]) == 0:
            print('Неверно заданы часы')
            return False
        for c in s[0]:
            if not c.isdigit():
                print('Дата должна содержать только числа')
                return False
            if int(s[0]) > 23:
                print('Неверно заданы часы')
                return False
        if len(s[1]) == 0:
            print('Неверно заданы минуты')
            return False
        for c in s[1]:
            if not c.isdigit():
                print('Дата должна содержать только числа')
                return False
            if int(s[1]) > 59:
                print('Неверно заданы минуты')
                return False
    return True

#Удаление интерфейса
def DeleteRow():
    for selected_item in tree.selection():
        #Проверка на соединение и удаление
        print(f'API? Интерфейс удален')
        del server_interface[str(tree.item(selected_item)['values'][0])]
        tree.delete(selected_item)
    return

#Добавление интерфейса
def AddRowToTable():
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
        print(f'API? Добавлена строка: {row_val}')
        tree.insert('', END, values=row_val)
        server_interface[number] = {
            'weightIP/COM': COM,
            'model': model,
            'printerIP': IPp,
            'data': data,
            'time': time
        }
    return

#Изменение интерфейса
def ChangeRowFromData():
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
        print(f'API? Изменена строка: {row_val}')
        tree.item(last_select_row, values=row_val)
        server_interface[number] = {
            'weightIP/COM': COM,
            'model': model,
            'printerIP': IPp,
            'data': data,
            'time': time
        }
    return

#Заполнение полей из таблицы по нажатию строки
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
        print(f'Ошибка при нажатии в пустое метсо таблицы или заголовок {e}')

with open("config.json", 'r') as file:
    _config_params = json.load(file)
host = _config_params['server']['host']
port = _config_params['server']['port']

last_select_row = ''

main_window = Tk()
main_window.title("Управление интерфейсами")
main_window.geometry("815x500+550+200")
main_window.wm_minsize(815,500)
main_window.rowconfigure(index=0, weight=1)
main_window.columnconfigure(index=0, weight=1)

interface_frame = LabelFrame(main_window, text='Список интерфейсов')
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

button_frame = LabelFrame(main_window, text='Управление')
button_frame.grid(row=0, column=1, sticky="nsew", padx=2)
btn_update = Button(button_frame, text="Обновить", command=UpdateInterface)
btn_update.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
btn_save = Button(button_frame, text="Перезапустить интерфейсы", command=ReloadInterfaces)
btn_save.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
btn_reload = Button(button_frame, text="Перезапустить интерфейсы")
btn_reload.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
btn_models = Button(button_frame, text="Модели")
btn_models.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
#Поле собственного IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
label = Label(main_window, text=f'Текущий IP: {s.getsockname()[0]}')
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
server_models = dict({
    "CAS HD 60": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    },
    "CKE-60-4050": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    },
    "CAS DB-150 H": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    },
    "CAS XE-6000": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    },
    "CAS CBL-220 H": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    },
    "ABCD": {
        "baudrate": 9600,
        "bytesize": 8,
        "timeout": 2
    }
})
models = list()
for key in server_models.keys():
    models.append(key)
models_drop = ttk.Combobox(enter_interface_frame ,values=models, justify=CENTER)
models_drop.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)
IPp_Label = Label(enter_interface_frame, text='IP принтера:', anchor='w' ,font=("Arial", 10))
IPp_Label.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
IPp_entry = Entry(enter_interface_frame, justify=CENTER)
IPp_entry.grid(row=3, column=1, sticky="nsew", padx=5, pady=2)
data_Label = Label(enter_interface_frame, text='Дата(dd.mm.yyyy):', anchor='w' ,font=("Arial", 10))
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

main_window.mainloop()

'''try:
    resp = requests.get(f"http://{host}:{port}/models")
    print(resp.status_code)
    print(resp.text)
    resp = requests.get(f"http://{host}:{port}/interfaces")
    print(resp.text)
except Exception as e:
    print(e)'''