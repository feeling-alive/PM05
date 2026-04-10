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

    def get_roles():
        cur.execute("SELECT id, role_name FROM roles ORDER BY id")
        return cur.fetchall()

    def load_users():
        for row in tree.get_children():
            tree.delete(row)
        cur.execute(
            "SELECT u.id, u.login, r.role_name, u.is_blocked "
            "FROM users u LEFT JOIN roles r ON u.role_id = r.id"
        )
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
        roles = get_roles()
        role_names = [r[1] for r in roles]
        e_role = ttk.Combobox(win, values=role_names, state="readonly")
        e_role.pack()

        def save():
            cur.execute("SELECT 1 FROM users WHERE login=%s", (e_login.get(),))
            if cur.fetchone():
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
                return
            role_id = next((rid for rid, name in roles if name == e_role.get()), None)
            cur.execute(
                "INSERT INTO users (login, password, role_id) VALUES (%s,%s,%s)",
                (e_login.get(), e_pass.get(), role_id)
            )
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
        user_id, login, role_name, blocked = user_data
        role_name = role_name if role_name else 'user'
        
        win = tk.Toplevel(panel)
        win.title("Редактирование пользователя")
        
        tk.Label(win, text="Логин:").pack()
        e_login = tk.Entry(win)
        e_login.insert(0, login)
        e_login.pack()
        
        tk.Label(win, text="Роль:").pack()
        roles = get_roles()
        role_names = [r[1] for r in roles]
        e_role = ttk.Combobox(win, values=role_names, state="readonly")
        e_role.set(role_name)
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
            
            role_id = next((rid for rid, name in roles if name == new_role), None)
            if new_pass:
                cur.execute(
                    "UPDATE users SET login=%s, role_id=%s, password=%s WHERE id=%s",
                    (new_login, role_id, new_pass, user_id)
                )
            else:
                cur.execute(
                    "UPDATE users SET login=%s, role_id=%s WHERE id=%s",
                    (new_login, role_id, user_id)
                )
            
            conn.commit()
            messagebox.showinfo("Успех", "Данные пользователя обновлены")
            win.destroy()
            load_users()
        
        tk.Button(win, text="Сохранить", command=save).pack(pady=5)


    tk.Button(panel, text="Добавить пользователя", command=add_user).pack(pady=5)
    tk.Button(panel, text="Редактировать пользователя", command=edit_user).pack(pady=5)
    tk.Button(panel, text="Снять блокировку", command=unblock_user).pack(pady=5)
    load_users()


def cap(username, is_admin=False):
    capcha_window = tk.Toplevel(root)
    capcha_window.title("Капча - Собери пазл")
    capcha_window.geometry("300x350")
    img1 = Image.open("1.png").resize((80, 80))
    img2 = Image.open("2.png").resize((80, 80))
    img3 = Image.open("3.png").resize((80, 80))
    img4 = Image.open("4.png").resize((80, 80))
    fragments = [img1, img2, img3, img4]
    current_order = list(range(4))
    random.shuffle(current_order)
    tk.Label(capcha_window, text="Собери пазл", font=("Arial", 12)).pack(pady=10)
    puzzle_frame = tk.Frame(capcha_window)
    puzzle_frame.pack(pady=10)
    buttons = []
    photo_images = []
    selected = [None]
    
    def create_buttons():
        for widget in puzzle_frame.winfo_children():
            widget.destroy()
        buttons.clear()
        photo_images.clear()
        for pos, frag_idx in enumerate(current_order):
            img_tk = ImageTk.PhotoImage(fragments[frag_idx])
            photo_images.append(img_tk)
            btn = tk.Button(puzzle_frame, image=img_tk, command=lambda p=pos: on_click(p), bd=0, highlightthickness=0)
            btn.image = img_tk
            if pos < 2:
                btn.grid(row=0, column=pos, padx=2, pady=2)
            else:
                btn.grid(row=1, column=pos-2, padx=2, pady=2)
            buttons.append(btn)
    
    def on_click(pos):
        if selected[0] is None:
            selected[0] = pos
        else:
            current_order[selected[0]], current_order[pos] = current_order[pos], current_order[selected[0]]
            selected[0] = None
            create_buttons()
    
    def check():
        if current_order == [0, 1, 2, 3]:
            messagebox.showinfo("Успех", "Пазл собран правильно!")
            cur.execute("UPDATE users SET fail_count = 0 WHERE login = %s", (username,))
            conn.commit()
            capcha_window.destroy()
            if is_admin:
                root.withdraw()
                admin_panel()
            else:
                messagebox.showinfo("Вход", f"Добро пожаловать, {username}!")
        else:
            messagebox.showerror("Ошибка", "Пазл собран неправильно!")
            cur.execute("UPDATE users SET fail_count = fail_count + 1 WHERE login = %s", (username,))
            cur.execute("SELECT fail_count FROM users WHERE login = %s", (username,))
            result = cur.fetchone()
            if result and result[0] >= 3:
                cur.execute("UPDATE users SET is_blocked = True WHERE login = %s", (username,))
            conn.commit()
            capcha_window.destroy()
    create_buttons()
    tk.Button(capcha_window, text="Проверить", command=check, bg="green", fg="white", font=("Arial", 11)).pack(pady=10)

def log():
    username = login.get()
    password = ps.get()
    
    if not username or not password:
        messagebox.showerror("Ошибка", "Заполните все поля, пожалуйста")
        return
    
    cur.execute("SELECT is_blocked, fail_count FROM users WHERE login = %s", (username,))
    user_check = cur.fetchone()
    
    if user_check and user_check[0]:  # Если заблокирован
        messagebox.showerror("Ошибка", "Ваша учетная запись заблокирована. Обратитесь к администратору для разблокировки.")
        return
    
    cur.execute(
        "SELECT u.id, u.login, u.password, u.role_id, u.is_blocked, u.fail_count, r.role_name "
        "FROM users u LEFT JOIN roles r ON u.role_id = r.id "
        "WHERE u.login = %s AND u.password = %s",
        (username, password)
    )
    user = cur.fetchone()
    
    if not user:
        cur.execute("UPDATE users SET fail_count = fail_count + 1 WHERE login = %s", (username,))
        cur.execute("SELECT fail_count FROM users WHERE login = %s", (username,))
        fail_result = cur.fetchone()
        
        if fail_result and fail_result[0] >= 3:
            cur.execute("UPDATE users SET is_blocked = True WHERE login = %s", (username,))
            conn.commit()
            messagebox.showerror("Ошибка", "Неверный логин или пароль.\nВы превысили количество попыток. Учетная запись заблокирована.")
            return
        
        conn.commit()
        messagebox.showerror("Ошибка", "Неверный логин или пароль. Попробуйте еще раз.")
        return

    if user[6] == 'admin':
        cap(username, is_admin=True)
    else:
        cap(username, is_admin=False)

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