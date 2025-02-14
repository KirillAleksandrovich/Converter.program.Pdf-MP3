from gtts import gTTS
import pdfplumber
from pathlib import Path
from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog
from tkinter import ttk
import threading
import os

# Глобальные переменные для управления процессом конвертации
is_converting = False
stop_conversion = False


def pdf_to_mp3(file_path, language, output_dir):
    global stop_conversion
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

        return f'Файл успешно сохранён: {output_path}'
    else:
        return 'Ошибка: Файл не выбран или не является PDF!'


def update_progress(value):
    progress_bar['value'] = value
    root.update_idletasks()


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
        progress_bar['value'] = 0

        threading.Thread(target=perform_conversion, args=(file_path, language, output_dir)).start()
    else:
        mb.showwarning("Ошибка", "Заполните все поля!")


def perform_conversion(file_path, language, output_dir):
    global is_converting, stop_conversion
    result = pdf_to_mp3(file_path, language, output_dir)
    is_converting = False

    root.after(0, lambda: [
        button_convert.config(state=NORMAL),
        button_cancel.config(state=DISABLED),
        progress_bar.config(value=0),
        mb.showinfo("Готово", "Конвертация завершена!" if "успешно" in result else result)
    ])


def cancel_conversion():
    global stop_conversion
    if is_converting:
        stop_conversion = True
        button_convert.config(state=NORMAL)
        button_cancel.config(state=DISABLED)
        progress_bar['value'] = 0
        mb.showinfo("Отмена", "Конвертация прервана")


# Создание GUI
root = Tk()
root.title("PDF to MP3 Converter")
root.geometry("600x250")

# Элементы управления
Label(root, text="PDF файл:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
entry_file_path = Entry(root, width=50)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)
Button(root, text="Обзор", command=select_file).grid(row=0, column=2, padx=5, pady=5)

Label(root, text="Язык:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
combo_language = ttk.Combobox(root, values=["ru", "en"], width=47)
combo_language.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=EW)
combo_language.set("ru")

Label(root, text="Папка для сохранения:").grid(row=2, column=0, padx=10, pady=5, sticky=W)
entry_output_dir = Entry(root, width=50)
entry_output_dir.grid(row=2, column=1, padx=5, pady=5)
Button(root, text="Обзор", command=select_output_dir).grid(row=2, column=2, padx=5, pady=5)

button_convert = Button(root, text="Конвертировать", command=start_conversion)
button_convert.grid(row=3, column=1, pady=10, sticky=EW)

button_cancel = Button(root, text="Отмена", command=cancel_conversion, state=DISABLED)
button_cancel.grid(row=3, column=2, pady=10, padx=5, sticky=EW)

progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=550, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()