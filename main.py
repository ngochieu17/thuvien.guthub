import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import sys
import thuvien 
from tkinter import ttk
import re


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
        if len(username) < 6 or len(username) > 50:
            messagebox.showwarning("Tên đăng kí người dùng không hợp lệ", "Tên người dùng phải từ 6 đến 50 ký tự.")
            return
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{5,49}$', username):
            messagebox.showwarning("Tên đăng nhập không hợp lệ",
            "Tên đăng nhập chỉ được chứa chữ cái, số, dấu gạch dưới (_), và phải bắt đầu bằng chữ.")
            return
        if len(password) < 6 or len(password)>20:
            messagebox.showwarning("Mật khẩu yếu", "Mật khẩu phải có ít nhất 6 đến 20 kí tự.")
            return

        users = load_users()
        if any(u["username"] == username for u in users):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")  
            return

        users.append({"username": username, "password": password, "role": role})
        save_users(users)
        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        reg_win.destroy()

    tk.Button(reg_win, text="Đăng ký", command=confirm_register).pack(pady=10)

# ----- Quản lý người dùng (admin) -----
def quan_ly_nguoi_dung():
    user_win= tk.Toplevel()
    user_win.title("Quản lý người dùng")
    user_win.geometry("700x500")

    tk.Label(user_win, text="Danh sách người dùng", font=("Arial", 14)).pack(pady=10)

    tree = ttk.Treeview(user_win, columns=("username", "password", "role"), show="headings")
    tree.heading("username", text="Tên đăng nhập")
    tree.heading("password", text="Mật khẩu")
    tree.heading("role", text="Quyền")
    tree.column("username", width=200)
    tree.column("password", width=200)
    tree.column("role", width=100)
    tree.pack(fill="both", expand=True)

    #listbox = tk.Listbox(user_win)
    #listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_tree():
        tree.delete(*tree.get_children())
        for user in load_users():
            tree.insert("", "end", values=(user["username"], user["password"], user["role"]))

    def xoa_user():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng cần xóa.")
            return
        item = tree.item(selected)
        username = item["values"][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"):
            users = load_users()
            users = [u for u in users if u["username"] != username]
            save_users(users)
            load_tree()
            messagebox.showinfo("Thành công", f"Đã xóa người dùng: {username}")
    def sua_nguoi_dung():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng cần sửa.")
            return
        item = tree.item(selected)
        old_username = item["values"][0]
        old_password = item["values"][1]
        old_role = item["values"][2]

        top = tk.Toplevel()
        top.title("Sửa người dùng")
        top.geometry("300x250")

        tk.Label(top, text="Tên đăng nhập").pack(pady=5)
        entry_username = tk.Entry(top)
        entry_username.insert(0, old_username)
        entry_username.pack()

        tk.Label(top, text="Mật khẩu").pack(pady=5)
        entry_password = tk.Entry(top)
        entry_password.insert(0, old_password)
        entry_password.pack()

        tk.Label(top, text="Quyền (user/admin)").pack(pady=5)
        entry_role = tk.Entry(top)
        entry_role.insert(0, old_role)
        entry_role.pack()
        
        def luu_thay_doi():
            global info_win,tree_info

            new_username = entry_username.get().strip()
            new_password = entry_password.get().strip()
            new_role = entry_role.get().strip()
            if not all([new_username, new_password, new_role]):
                messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin.")
                return
            users = load_users()
            for u in users:
                if u["username"] == old_username:
                    u["username"] = new_username
                    u["password"] = new_password
                    u["role"] = new_role
                    break
            save_users(users)
            load_tree()
            
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin người dùng.")
            if info_win and info_win.winfo_exists():
                # Xóa dữ liệu cũ trong TreeView và thêm dữ liệu mới
                for i in tree_info.get_children():
                    tree_info.delete(i)
                for user in users:
                    tree_info.insert("", "end", values=(user["username"], user["password"], user["role"]))
                info_win.deiconify()  
                info_win.lift()      
            else:
                # Tạo cửa sổ mới
                info_win = tk.Toplevel(top)
                info_win.title("Danh sách người dùng hiện tại")
                info_win.geometry("500x400")
                
                tree_info = ttk.Treeview(info_win, columns=("username", "password", "role"), show="headings")
                tree_info.heading("username", text="Tên đăng nhập")
                tree_info.heading("password", text="Mật khẩu")
                tree_info.heading("role", text="Quyền")
                tree_info.column("username", width=180)
                tree_info.column("password", width=180)
                tree_info.column("role", width=100)
                tree_info.pack(fill="both", expand=True, padx=10, pady=10)

                for user in users:
                    tree_info.insert("", "end", values=(user["username"], user["password"], user["role"]))
        tk.Button(top, text="Lưu", command=luu_thay_doi).pack(pady=10)    
    def them_user():
        top = tk.Toplevel(user_win)
        top.title("Thêm người dùng")
        top.geometry("300x250")

        tk.Label(top, text="Tên đăng nhập").pack(pady=5)
        entry_username = tk.Entry(top)
        entry_username.pack()

        tk.Label(top, text="Mật khẩu").pack(pady=5)
        entry_password = tk.Entry(top)
        entry_password.pack()

        tk.Label(top, text="Quyền (user/admin)").pack(pady=5)
        entry_role = tk.Entry(top)
        entry_role.pack()

        def luu_user_moi():
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            role = entry_role.get().strip()
            if not all([username, password, role]):
                messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin.")
                return
            if len(password) < 6 or len(password)>20:
                messagebox.showwarning("Mật khẩu yếu", "Mật khẩu phải có ít nhất 6 đến 20 kí tự.")
                return
            users = load_users()
            if any(u["username"] == username for u in users):
                messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
                return
            users.append({"username": username, "password": password, "role": role})
            save_users(users)
            load_tree()
            top.destroy()
            messagebox.showinfo("Thành công", "Đã thêm người dùng mới.")

        tk.Button(top, text="Lưu", command=luu_user_moi).pack(pady=10)
    def quay_lai_dang_nhap():
        user_win.destroy()
        root.deiconify()  # Hiện lại cửa sổ đăng nhập

    tk.Button(user_win, text="⬅️ Thoát", command=quay_lai_dang_nhap).pack(pady=10)

    btn_frame = tk.Frame(user_win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="➕ Thêm", command=them_user).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="✏️ Sửa", command=sua_nguoi_dung).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="❌ Xóa", command=xoa_user).pack(side=tk.LEFT, padx=5)

    load_tree()

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
    return None 

# ----- Main -----
def main():
    while True:
        login_result = show_login_window()
        if login_result is None:
            print("Người dùng đã đóng cửa sổ hoặc đăng nhập thất bại.")
            break
        username, role = login_result
        #if role == "admin":
            #quan_ly_nguoi_dung()
            #continue

        import thuvien
        logout = thuvien.launch_app(username, role)  

        if not logout:
            # Người dùng đăng xuất, tiếp tục vòng lặp để đăng nhập lại
            continue
        else:
            # Người dùng thoát hẳn, thoát vòng lặp
            break

if __name__ == "__main__":
    main()
   

