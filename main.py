import sqlite3
import random
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "arrays.db"


# ---------------------- База данных ----------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_arrays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            arr TEXT NOT NULL,
            sorted_or_not BOOLEAN NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def register_user(login, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (login, password) VALUES (?, ?)", (login, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authorize_user(login, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE login=? AND password=?", (login, password))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def load_user_arrays(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT arr FROM user_arrays WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def save_array(user_id, arr, sorted_or_not):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_arrays (user_id, arr, sorted_or_not) VALUES (?, ?, ?)",
        (user_id, ",".join(map(str, arr)), sorted_or_not)
    )
    conn.commit()
    conn.close()


def clear_array(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM user_arrays WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ---------------------- Алгоритм сортировки (вставками) ----------------------

def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a

# ---------------------- GUI ----------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Работа с массивами")
        self.geometry("250x220")
        self.user_id = None
        self.show_login()

    # ---------- Авторизация ----------
    def show_login(self):
        self.clear()

        ttk.Label(self, text="Логин").pack(pady=5)
        login_entry = ttk.Entry(self)
        login_entry.pack()

        ttk.Label(self, text="Пароль").pack(pady=5)
        password_entry = ttk.Entry(self, show="*")
        password_entry.pack()

        def login():
            uid = authorize_user(login_entry.get(), password_entry.get())
            if uid:
                self.user_id = uid
                self.show_main()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")

        def register():
            if register_user(login_entry.get(), password_entry.get()):
                messagebox.showinfo("Успех", "Пользователь зарегистрирован")
            else:
                messagebox.showerror("Ошибка", "Логин уже существует")

        ttk.Button(self, text="Войти", command=login).pack(pady=5)
        ttk.Button(self, text="Регистрация", command=register).pack()

    def save_arr(self, arr, sorted_or_not):
        save_array(self.user_id, arr, sorted_or_not)
        self.refresh_table()
        messagebox.showinfo("Сохранено", f"Массив сохранён: {arr}")

    # ---------- Основное окно ----------
    def show_main(self):
        self.clear()
        self.geometry("900x600")

        input_frame = ttk.LabelFrame(self, text="Ввод массива")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.array_entry = ttk.Entry(input_frame)
        self.array_entry.pack(fill=tk.X, padx=5, pady=5)

        # Кнопки: Ввести и Генерация
        ttk.Button(input_frame, text="Ввести", command=self.input_array).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Сгенерировать случайный массив", command=self.generate_array).pack(side=tk.LEFT,
                                                                                                         padx=5)

        self.current_array = None
        self.sorted_array = None

        # Frame для кнопок сортировки и сохранения после ввода
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill=tk.X, padx=10, pady=5)

        # Таблица с массивами, постоянная в основном окне
        self.tree = ttk.Treeview(self, columns=("data", "sorted"), show="headings")
        self.tree.heading("data", text="Массив")
        self.tree.heading("sorted", text="Отсортирован")
        self.tree.column("data", width=500)
        self.tree.column("sorted", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree.bind("<Double-1>", self.copy_array_from_table)

        self.refresh_table()

        ttk.Button(self, text="Очистить все массивы", command=self.clear_user_arrays).pack(pady=5)
        ttk.Button(self, text="Справка", command=self.show_help).pack(pady=5)
        ttk.Button(self, text="Выйти", command=self.show_login).pack(pady=5)

    # Метод ввода массива (с поля)
    def input_array(self):
        text = self.array_entry.get().strip()

        # Проверка на пустой ввод
        if not text:
            messagebox.showwarning(
                "Пустой массив",
                "Массив пуст. Введите целые числа через пробел или сгенерируйте массив."
            )
            return
        try:
            arr = list(map(int, self.array_entry.get().split()))
            self.current_array = arr

            # Очистка старых кнопок
            for widget in self.action_frame.winfo_children():
                widget.destroy()

            # Кнопки сортировки и сохранения
            ttk.Button(self.action_frame, text="Отсортировать", command=self.sort_array).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.action_frame, text="Сохранить массив",
                       command=lambda: self.save_arr(self.current_array, False)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа через пробел")

    # Метод генерации случайного массива (просто заполняет поле)
    def generate_array(self):
        arr = [random.randint(-100, 100) for _ in range(random.randint(5, 15))]
        self.array_entry.delete(0, tk.END)
        self.array_entry.insert(0, " ".join(map(str, arr)))

    def copy_array_from_table(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        array_str = values[0]  # строка вида "1,2,3,-5"

        # Преобразуем формат: запятые → пробелы
        array_with_spaces = array_str.replace(",", " ")

        self.array_entry.delete(0, tk.END)
        self.array_entry.insert(0, array_with_spaces)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT arr, sorted_or_not FROM user_arrays WHERE user_id=?", (self.user_id,))
        for r in cur.fetchall():
            self.tree.insert("", tk.END, values=(r[0], "Да" if r[1] else "Нет"))
        conn.close()


    def sort_array(self):
        if self.current_array is None:
            messagebox.showwarning("Внимание", "Сначала введите массив")
            return

        # Сортируем массив и заменяем содержимое поля ввода
        self.sorted_array = insertion_sort(self.current_array)
        self.array_entry.delete(0, tk.END)
        self.array_entry.insert(0, " ".join(map(str, self.sorted_array)))

        # Обновляем кнопки: теперь можно сохранить отсортированный массив
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        ttk.Button(self.action_frame, text="Сохранить отсортированный массив",
                   command=lambda: self.save_arr(self.sorted_array, True)).pack(side=tk.LEFT, padx=5)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_user_arrays(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить все массивы?"):
            clear_array(self.user_id)
            self.refresh_table()

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Справка")
        help_window.geometry("500x400")
        help_window.resizable(False, False)

        text = (
            "Приложение предназначено для работы с массивами целых чисел и базой данных.\n\n"

            "Основные возможности:\n"
            "• Регистрация и авторизация пользователя.\n"
            "• Ввод массива целых чисел вручную.\n"
            "• Генерация случайного массива целых чисел.\n"
            "• Сортировка массива алгоритмом вставок.\n"
            "• Сохранение исходного и отсортированного массивов.\n"
            "• Просмотр сохранённых массивов пользователя.\n"
            "• Очистка базы данных пользователя.\n\n"

            "Порядок работы:\n"
            "1. Введите массив вручную или сгенерируйте случайный.\n"
            "2. Нажмите кнопку «Ввести».\n"
            "3. При необходимости отсортируйте массив.\n"
            "4. Сохраните исходный или отсортированный массив.\n\n"

            "Формат ввода массива:\n"
            "Целые числа, разделённые пробелами.\n"
            "Пример: 5 -3 10 8 0"
        )

        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(expand=True, fill=tk.BOTH)

        ttk.Button(help_window, text="Закрыть", command=help_window.destroy).pack(pady=10)


if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
