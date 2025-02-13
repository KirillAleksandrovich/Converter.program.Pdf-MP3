from gtts import gTTS
import pdfplumber
from pathlib import Path
from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog
from tkinter import ttk
import threading
import os
import time

# Глобальные переменные для управления процессом конвертации
is_converting = False
stop_conversion = False

def pdf_to_mp3(file_path, language, output_dir):
    global is_converting, stop_conversion
    if Path(file_path).is_file() and Path(file_path).suffix == '.pdf':
        print(f'[+] Original file: {Path(file_path).name}')
        print(f'[+] Processing...')

        # Этап 1: Чтение PDF
        update_progress(25)
        if stop_conversion:
            return "Конвертация отменена"
        with pdfplumber.PDF(open(file=file_path, mode='rb')) as pdf:
            pages = [page.extract_text() for page in pdf.pages]

        # Этап 2: Извлечение текста
        update_progress(50)
        if stop_conversion:
            return "Конвертация отменена"
        text = ''.join(pages)
        text = text.replace('\n', '')

        # Этап 3: Генерация аудио
        update_progress(75)
        if stop_conversion:
            return "Конвертация отменена"
        my_audio = gTTS(text=text, lang=language, slow=False)

        # Этап 4: Сохранение файла
        update_progress(100)
        if stop_conversion:
            return "Конвертация отменена"
        file_name = Path(file_path).stem
        output_path = os.path.join(output_dir, f'{file_name}.mp3')
        my_audio.save(output_path)

        return f'[+] Файл успешно сохранён: {output_path}'
    else:
        return 'Такого файла нет!'

def update_progress(value):
    progress_bar['value'] = value
    root.update_idletasks()  # Обновление интерфейса

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    entry_file_path.delete(0, END)
    entry_file_path.insert(0, file_path)

def select_output_dir():
    output_dir = filedialog.askdirectory()
    entry_output_dir.delete(0, END)
    entry_output_dir.insert(0, output_dir)

def start_conversion():
    global is_converting, stop_conversion
    if is_converting:
        mb.showwarning("Ошибка", "Конвертация уже выполняется!")
        return

    file_path = entry_file_path.get()
    language = combo_language.get()
    output_dir = entry_output_dir.get()
    if file_path and language and output_dir:
        is_converting = True
        stop_conversion = False
        button_convert.config(state=DISABLED)
        button_cancel.config(state=NORMAL)
        progress_bar['value'] = 0  # Сброс прогресс-бара

        # Запуск конвертации в отдельном потоке
        threading.Thread(target=perform_conversion, args=(file_path, language, output_dir)).start()
    else:
        mb.showwarning("Ошибка", "Пожалуйста, выберите файл, укажите язык и папку для сохранения")

def perform_conversion(file_path, language, output_dir):
    global is_converting, stop_conversion
    result = pdf_to_mp3(file_path, language, output_dir)
    is_converting = False
    button_convert.config(state=NORMAL)
    button_cancel.config(state=DISABLED)
    if not stop_conversion:
        mb.showinfo("Результат", result)

def cancel_conversion():
    global stop_conversion
    if is_converting:
        stop_conversion = True
        mb.showinfo("Отмена", "Конвертация отменена.")
        button_convert.config(state=NORMAL)
        button_cancel.config(state=DISABLED)

# Создание основного окна
root = Tk()
root.title("PDF to MP3 Converter")

# Создание и размещение элементов управления
label_file_path = Label(root, text="Выберите PDF файл:")
label_file_path.grid(row=0, column=0, padx=10, pady=10)

entry_file_path = Entry(root, width=50)
entry_file_path.grid(row=0, column=1, padx=10, pady=10)

button_browse = Button(root, text="Обзор", command=select_file)
button_browse.grid(row=0, column=2, padx=10, pady=10)

label_language = Label(root, text="Язык:")
label_language.grid(row=1, column=0, padx=10, pady=10)

combo_language = ttk.Combobox(root, values=["ru", "en"], width=47)
combo_language.grid(row=1, column=1, padx=10, pady=10)
combo_language.current(0)  # Установка значения по умолчанию

label_output_dir = Label(root, text="Папка для сохранения:")
label_output_dir.grid(row=2, column=0, padx=10, pady=10)

entry_output_dir = Entry(root, width=50)
entry_output_dir.grid(row=2, column=1, padx=10, pady=10)

button_output_dir = Button(root, text="Обзор", command=select_output_dir)
button_output_dir.grid(row=2, column=2, padx=10, pady=10)

button_convert = Button(root, text="Конвертировать", command=start_conversion)
button_convert.grid(row=3, column=1, padx=10, pady=10)

button_cancel = Button(root, text="Отмена", command=cancel_conversion, state=DISABLED)
button_cancel.grid(row=3, column=2, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Запуск основного цикла обработки событий
root.mainloop()