import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from PIL import Image, ImageTk
import random

conn = psycopg2.connect(
    host='localhost',
    database='Practice',
    user='postgres',
    password='123123',
    port='5432')
cur = conn.cursor()


def admin_panel():
    panel = tk.Toplevel(root)
    panel.title("Панель администратора")
    panel.geometry("1200x600")
    tree = ttk.Treeview(panel, columns=("id","login","role","blocked"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("login", text="Логин")
    tree.heading("role", text="Роль")
    tree.heading("blocked", text="Заблокирован")
    tree.pack(pady=10)

    def load_users():
        for row in tree.get_children():
            tree.delete(row)
        cur.execute("SELECT id, login, role, is_blocked FROM users")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)

    def add_user():
        win = tk.Toplevel(panel)
        tk.Label(win, text="Логин:").pack()
        e_login = tk.Entry(win)
        e_login.pack()
        tk.Label(win, text="Пароль:").pack()
        e_pass = tk.Entry(win)
        e_pass.pack()
        tk.Label(win, text="Роль:").pack()
        e_role = ttk.Combobox(win, values=["user", "admin"], state="readonly")
        e_role.pack()

        def save():
            cur.execute("SELECT 1 FROM users WHERE login=%s", (e_login.get(),))
            if cur.fetchone():
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
                return
            cur.execute("INSERT INTO users (login, password, role) VALUES (%s,%s,%s)",
                       (e_login.get(), e_pass.get(), e_role.get()))
            conn.commit()
            messagebox.showinfo("Успех", "Пользователь добавлен")
            win.destroy()
            load_users()

        tk.Button(win, text="Сохранить", command=save).pack(pady=5)

    def unblock_user():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        user_id = tree.item(selected[0])["values"][0]
        cur.execute("UPDATE users SET is_blocked=False, fail_count=0 WHERE id=%s", (user_id,))
        conn.commit()
        messagebox.showinfo("Успех", "Пользователь разблокирован")
        load_users()

    def edit_user():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        user_data = tree.item(selected[0])["values"]
        user_id, login, role, blocked = user_data
        
        win = tk.Toplevel(panel)
        win.title("Редактирование пользователя")
        
        tk.Label(win, text="Логин:").pack()
        e_login = tk.Entry(win)
        e_login.insert(0, login)
        e_login.pack()
        
        tk.Label(win, text="Роль:").pack()
        e_role = ttk.Combobox(win, values=["user", "admin"], state="readonly")
        e_role.set(role)
        e_role.pack()
        
        tk.Label(win, text="Новый пароль (оставить пусто, чтобы не менять):").pack()
        e_pass = tk.Entry(win)
        e_pass.pack()
        
        def save():
            new_login = e_login.get()
            new_role = e_role.get()
            new_pass = e_pass.get()
            
            if not new_login or not new_role:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            if new_login != login:
                cur.execute("SELECT 1 FROM users WHERE login=%s AND id!=%s", (new_login, user_id))
                if cur.fetchone():
                    messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
                    return
            
            if new_pass:
                cur.execute("UPDATE users SET login=%s, role=%s, password=%s WHERE id=%s",
                           (new_login, new_role, new_pass, user_id))
            else:
                cur.execute("UPDATE users SET login=%s, role=%s WHERE id=%s",
                           (new_login, new_role, user_id))
            
            conn.commit()
            messagebox.showinfo("Успех", "Данные пользователя обновлены")
            win.destroy()
            load_users()
        
        tk.Button(win, text="Сохранить", command=save).pack(pady=5)


    tk.Button(panel, text="Добавить пользователя", command=add_user).pack(pady=5)
    tk.Button(panel, text="Редактировать пользователя", command=edit_user).pack(pady=5)
    tk.Button(panel, text="Снять блокировку", command=unblock_user).pack(pady=5)
    load_users()


def check(clicked, correct, capcha, is_admin=False):
    if clicked == correct:
        messagebox.showinfo("Успех", 'Вы прошли капчу')
        capcha.destroy()
        if is_admin:
            root.withdraw()
            admin_panel()
    else:
        messagebox.showerror("Ошибка",'Неверно, попробуйте еще раз')


def cap(is_admin=False):
    capcha = tk.Toplevel(root)
    imgo1 = Image.open("1.png")
    imgo1 = imgo1.resize((100,100))
    imgo2 = Image.open("2.png")
    imgo2 = imgo2.resize((100,100))
    imgo3 = Image.open("3.png")
    imgo3 = imgo3.resize((100,100))
    imgo4 = Image.open("4.png")
    imgo4 = imgo4.resize((100,100))
    img1 = ImageTk.PhotoImage(imgo1)
    img2 = ImageTk.PhotoImage(imgo2)
    img3 = ImageTk.PhotoImage(imgo3)
    img4 = ImageTk.PhotoImage(imgo4)
    images = [img1, img2, img3, img4]
    row2 = tk.Frame(capcha)
    correct = random.randint(1, 4)
    tr = tk.Label(row2, image=images[correct - 1])
    tr.image = images[correct - 1]
    tr.pack(side="top")
    row2.pack()
    row1 = tk.Frame(capcha)
    row3 = tk.Frame(capcha)
    label = tk.Label(row1, image=img1)
    label.image = img1
    label.bind("<Button-1>", lambda e: check(1, correct, capcha, is_admin))
    label.pack(side='left')
    label2 = tk.Label(row1, image=img2)
    label2.image = img2
    label2.bind("<Button-1>", lambda e: check(2, correct, capcha, is_admin))
    label2.pack(side="left")
    label3 = tk.Label(row3, image=img3)
    label3.image = img3
    label3.bind("<Button-1>", lambda e: check(3, correct, capcha, is_admin))    
    label3.pack(side='left')
    label4 = tk.Label(row3, image=img4)
    label4.image = img4
    label4.bind("<Button-1>", lambda e: check(4, correct, capcha, is_admin))    
    label4.pack(side="left")
    row1.pack()
    row3.pack()

def log():
    print(login.get())
    print(ps.get())
    if not login.get() or not ps.get():
        messagebox.showerror("Ошибка", "Заполните все поля, пожалуйста")
        return
    cur.execute("SELECT is_blocked FROM users WHERE login = %s", (login.get(),))
    Blocked = cur.fetchone()
    if Blocked and Blocked[0]:
        messagebox.showerror("Ошибка", "Вы заблокированы. Обратитесь к администратору")
        return
    cur.execute("SELECT * FROM users WHERE login = %s AND password = %s", (login.get(), ps.get()))
    user = cur.fetchone()
    if not user:
        messagebox.showerror("Ошибка", "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные")
        cur.execute("UPDATE users SET fail_count = fail_count + 1 WHERE login = %s", (login.get(),))
        cur.execute("UPDATE users SET is_blocked = True WHERE fail_count >= 3 AND login = %s", (login.get(),))
        conn.commit()
        return
    else:
        if user[3] == 'admin': 
            cap(is_admin=True) 
        else:
            cap(is_admin=False)

root = tk.Tk()

root.title("Авторизация")
root.geometry("300x200")
tk.Label(root, text="Логин: ").pack()
login = tk.Entry(root)
login.pack()
tk.Label(root, text="Пароль: ").pack()
ps = tk.Entry(root, show="*")
ps.pack()
tk.Button(root, text="Войти", command=log).pack(padx=20, pady=20)

 
root.mainloop()