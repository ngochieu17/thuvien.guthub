import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import sys

USERS_FILE = "users.json"
BOOKS_FILE = "books.json"
# ----- Hàm lấy đường dẫn ảnh khi chuyển sang exe -----
def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối tới file khi chạy file exe hoặc script"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

USERS_FILE = resource_path("users.json")
HISTORY_FILE = resource_path("history.json")
BORROW_HISTORY_FILE = resource_path("borrow_history.json")  
BOOKS_FILE = resource_path("books.json")
BORROW_FILE = resource_path("borrow.json")
# ----- Load & Save -----
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ----- Đăng ký người dùng -----
def register():
    reg_win = tk.Toplevel(root)
    reg_win.title("Đăng ký tài khoản")
    reg_win.geometry("300x250")

    tk.Label(reg_win, text="Tên đăng nhập:").pack(pady=5)
    entry_user = tk.Entry(reg_win)
    entry_user.pack()

    tk.Label(reg_win, text="Mật khẩu:").pack(pady=5)
    entry_pass = tk.Entry(reg_win, show="*")
    entry_pass.pack()

    tk.Label(reg_win, text="Chọn quyền:").pack(pady=5)
    var_role = tk.StringVar(value="user")
    tk.Radiobutton(reg_win, text="Người dùng", variable=var_role, value="user").pack()

    def confirm_register():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        role = var_role.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ thông tin.")
            return
        if len(password) < 6:
            messagebox.showwarning("Mật khẩu yếu", "Mật khẩu phải có ít nhất 6 ký tự.")
            return

        users = load_users()
        if any(u["username"] == username for u in users):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")  # Đã sửa lỗi message-showerror
            return

        users.append({"username": username, "password": password, "role": role})
        save_users(users)
        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        reg_win.destroy()

    tk.Button(reg_win, text="Đăng ký", command=confirm_register).pack(pady=10)

# ----- Đăng nhập -----
def show_login_window():
    global root, username_entry, password_entry

    login_result = {"success": False, "username": None, "role": None}

    root = tk.Tk()
    root.title("🟦 QUẢN LÝ THƯ VIỆN - Đăng nhập")
    root.geometry("500x500")
    root.configure(bg="#eef7ff")


    def login():
        users = load_users()
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        for u in users:
            if u["username"] == username and u["password"] == password:
                messagebox.showinfo("Thành công", f"Xin chào {u['username']} ({u['role']})")
                login_result["success"] = True
                login_result["username"] = u["username"]
                login_result["role"] = u["role"]
                root.destroy()
                return
        messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")

    try:
        logo_path = resource_path("logo1.png")
        image = Image.open(logo_path)
        image = image.resize((100, 100))
        img = ImageTk.PhotoImage(image)
        label_img = tk.Label(root, image=img, bg="#eef7ff")
        label_img.image = img
        label_img.pack(pady=5)
    except Exception as e:
        messagebox.showwarning("Lỗi ảnh", f"Không thể tải logo: {e}")

    tk.Label(root, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 14, "bold"), bg="#eef7ff").pack(pady=10)
    tk.Label(root, text="Tên đăng nhập:", bg="#eef7ff").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Mật khẩu:", bg="#eef7ff").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Button(root, text="Đăng nhập", command=login).pack(pady=10)
    tk.Button(root, text="Đăng ký tài khoản", command=register).pack(pady=5)

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    if login_result["success"]:
        return login_result["username"], login_result["role"]
    return None  # Nếu người dùng thoát hoặc đăng nhập sai

# ----- Main -----
def main():
    while True:
        login_result = show_login_window()
        if login_result is None:
            print("Người dùng đã đóng cửa sổ hoặc đăng nhập thất bại.")
            break
        username, role = login_result

        import thuvien
        logout = thuvien.launch_app(username, role)  # Giả sử hàm này trả về True nếu logout, False nếu thoát hẳn

        if not logout:
            # Người dùng đăng xuất, tiếp tục vòng lặp để đăng nhập lại
            continue
        else:
            # Người dùng thoát hẳn, thoát vòng lặp
            break

if __name__ == "__main__":
    main()
   

