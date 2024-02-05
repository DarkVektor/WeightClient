from tkinter import *
from tkinter import ttk
import socket
#import flask
#from flask import Flask, jsonify, request
def FillTable(dict_interface):
    for key in dict_interface.keys():
        l = list()
        l.append(key)
        l.append(dict_interface[key]["weightIP/COM"])
        l.append(dict_interface[key]["model"])
        l.append(dict_interface[key]["printerIP"])
        l.append(dict_interface[key]["data"])
        l.append(dict_interface[key]["time"])
        tree.insert("", END, values=l)


#app = Flask(__name__)
'''
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    tasks = [
        {"id": 1, "title": "Task 1"},
        {"id": 2, "title": "Task 2"}
    ]
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)'''


server_interface = dict({
    "1": {
        "weightIP/COM": "COM1",
        "model": "CAS HD 60",
        "printerIP": "192.168.0.83:9100",
        "data": "",
        "time": ""
    },
    "2": {
        "weightIP/COM": "COM2",
        "model": "CAS HD 60",
        "printerIP": "192.168.0.83:9100",
        "data": "",
        "time": ""
    },
    "3": {
        "weightIP/COM": "COM3",
        "model": "CAS HD 60",
        "printerIP": "192.168.0.84:9100",
        "data": "",
        "time": ""
    },
    "4": {
        "weightIP/COM": "COM4",
        "model": "CAS HD 60",
        "printerIP": "192.168.0.83:9100",
        "data": "",
        "time": ""
    },
    "5": {
        "weightIP/COM": "COM5",
        "model": "CAS HD 60",
        "printerIP": "192.168.0.83:9100",
        "data": "",
        "time": ""
    }
})
main_window = Tk()
main_window.title("METANIT.COM")
main_window.geometry("803x500+100+100")
main_window.rowconfigure(index=0, weight=1)
main_window.columnconfigure(index=0, weight=1)

interface_frame = LabelFrame(main_window, text='Список интерфейсов')
interface_frame.grid(row=0, column=0, sticky="nsew", padx=2)

button_frame = LabelFrame(main_window, text='Управление')
button_frame.grid(row=0, column=1, sticky="nsew", padx=2)
btn_load = Button(button_frame, text="Загрузить конфигурацию")
btn_load.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
btn_save = Button(button_frame, text="Сохранить конфигурацию")
btn_save.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
btn_reload = Button(button_frame, text="Перезапустить интерфейсы")
btn_reload.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
btn_models = Button(button_frame, text="Модели")
btn_models.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
label = Label(main_window, text=f'Текущий IP: {s.getsockname()[0]}')
s.close()
label.grid(row=1, column=1, sticky="nsew", padx=5)

# определяем столбцы
columns = ("Number", "weightCOM_IP", "model", "PrinterIP", "Data", "Time")
tree = ttk.Treeview(interface_frame, columns=columns, show="headings")
tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
# определяем заголовки
tree.heading("Number", text="№", anchor=CENTER)
tree.heading("weightCOM_IP", text="COM/IP Весов", anchor=CENTER)
tree.heading("model", text="Модель", anchor=CENTER)
tree.heading("PrinterIP", text="IP Принтера", anchor=CENTER)
tree.heading("Data", text="Дата", anchor=CENTER)
tree.heading("Time", text="Время", anchor=CENTER)
tree.column("#1", stretch=YES, width=25, anchor=CENTER)
tree.column("#2", stretch=YES, width=100, anchor=CENTER)
tree.column("#3", stretch=YES, width=100, anchor=CENTER)
tree.column("#4", stretch=YES, width=100, anchor=CENTER)
tree.column("#5", stretch=YES, width=100, anchor=CENTER)
tree.column("#6", stretch=YES, width=100, anchor=CENTER)
#Заполнение таблицы
FillTable(server_interface)



# добавляем вертикальную прокрутку
#scrollbar = ttk.Scrollbar(orient=VERTICAL, command=tree.yview)
#tree.configure(yscroll=scrollbar.set)
#scrollbar.grid(row=0, column=1, sticky="ns")

main_window.mainloop()