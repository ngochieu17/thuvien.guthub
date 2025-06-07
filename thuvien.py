import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
import datetime
import requests
import sys
import subprocess
import re

from login_module import show_login_window
from main import quan_ly_nguoi_dung



BOOKS_FILE = "books.json"
BORROW_FILE = "borrow.json"
HISTORY_FILE = "history.json"

# Load/Save
def load_data(file):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#def tim_sach_tu_openlibrary(tieu_de):
    #try:
        #url = f"https://openlibrary.org/search.json?title={tieu_de}"
        #response = requests.get(url, timeout=5)
        #response.raise_for_status()
        #data = response.json()
        #docs = data.get("docs", [])
        #if docs:
            #sach = docs[0]
            #return {
                #"tieu_de": sach.get("title", "Không rõ"),
                #"tac_gia": ", ".join(sach.get("author_name", ["Không rõ"])),
                #"nam_xb": sach.get("first_publish_year", "Không rõ")
            #}
        #return None
    #except requests.RequestException as e:
        #messagebox.showerror("Lỗi", f"Không thể kết nối tới Open Library: {e}")
        #return None

# Xem danh sách
def view_books(tree):
    books = load_data(BOOKS_FILE)
    tree.delete(*tree.get_children())
    for b in books:
        tree.insert("", "end", values=(b["id"], b["title"], b["author"], b["year"], b.get("quantity", 0)))
def is_valid_book_id(book_id):
    return re.fullmatch(r'[B]\d{5}', book_id) is not None

# Thêm sách
def add_book(tree):
    top = tk.Toplevel()
    top.title("Thêm sách")
    top.geometry("300x300")

    tk.Label(top, text="ID.\nĐịnh dạng: B + 3 chữ số (VD: B001)").pack(pady=5)
    entry_id = tk.Entry(top)
    entry_id.pack()

    tk.Label(top, text="Tên sách").pack(pady=5)
    entry_title = tk.Entry(top)
    entry_title.pack()

    tk.Label(top, text="Tác giả").pack(pady=5)
    entry_author = tk.Entry(top)
    entry_author.pack()

    tk.Label(top, text="Năm").pack(pady=5)
    entry_year = tk.Entry(top)
    entry_year.pack()

    tk.Label(top, text="Số lượng").pack(pady=5)
    entry_quantity = tk.Entry(top)
    entry_quantity.insert(0, "1")
    entry_quantity.pack()

    #def tu_dong_dien():
        #tieu_de = entry_title.get().strip()
        #if not tieu_de:
            #messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên sách trước khi tìm.")
            #return
        #thong_tin = tim_sach_tu_openlibrary(tieu_de)
        #if thong_tin:
            #entry_title.delete(0, tk.END)
            #entry_title.insert(0, thong_tin["tieu_de"])
            #entry_author.delete(0, tk.END)
            #entry_author.insert(0, thong_tin["tac_gia"])
            #entry_year.delete(0, tk.END)
            #entry_year.insert(0, thong_tin["nam_xb"])
        #else:
            #messagebox.showinfo("Không tìm thấy", "Không tìm thấy thông tin cho sách này.")

    def save():
        id_val = entry_id.get().strip()
        title = entry_title.get().strip()
        author = entry_author.get().strip()
        year = entry_year.get().strip()
        # Tập ký tự bao gồm a-z, A-Z, số 0-9, khoảng trắng, các dấu . , ' - và các ký tự tiếng Việt có dấu
        pattern_vietnamese = r"[A-Za-z0-9\s\.,'\-ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯàáâãèéêìíòóôõùúăđĩũơưẠ-ỹ]+"
        #Kiểm tra định dạng ID:
        if not re.fullmatch(r'[B]\d{3}', id_val):
            messagebox.showerror("Lỗi", "Mã sách không hợp lệ.\nĐịnh dạng: B + 3 chữ số (VD: B001)")
            return
        # Kiểm tra tên sách hợp lệ, chiều dài 5-50 ký tự
        if not (5 <= len(title) <= 50):
            messagebox.showerror("Lỗi", "Tên sách phải có từ 5 đến 50 ký tự.")
            return
        if not re.fullmatch(pattern_vietnamese,title):
            messagebox.showerror("Lỗi", "Tên sách chỉ được chứa chữ cái, số, khoảng trắng và các dấu . , ' -")
            return
        # Kiểm tra tên tác giả hợp lệ, chiều dài 5-50 ký tự
        if not (5 <= len(author) <= 50):
            messagebox.showerror("Lỗi", "Tên tác giả phải có từ 5 đến 50 ký tự.")
            return
        if not re.fullmatch(pattern_vietnamese, author):
            messagebox.showerror("Lỗi", "Tên tác giả chỉ được chứa chữ cái, số, khoảng trắng và các dấu . , ' -")
            return
        # Kiểm tra năm hợp lệ (phải là số nguyên, không quá 2025)
        if not year.isdigit() or int(year) > 2025:
            messagebox.showerror("Lỗi", "Năm phải là số nguyên và không được lớn hơn 2025.")
            return

        try:
            quantity = int(entry_quantity.get())
            if quantity < 0:
                raise ValueError("Số lượng không hợp lệ")
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên không âm.")
            return
        
        if not all([id_val, title, author, year]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.")
            return
        books = load_data(BOOKS_FILE)

        if any(book["title"].lower()== title.lower() for book in books):
            messagebox.showerror("Lỗi", "Tên sách đã tồn tại.")
            return

        books = load_data(BOOKS_FILE)
        if any(b["id"] == id_val for b in books):
            messagebox.showerror("Trùng ID", "ID đã tồn tại.")
            return

        books.append({
            "id": id_val,
            "title": title,
            "author": author,
            "year": year,
            "quantity": quantity
        })
        save_data(BOOKS_FILE, books)
        top.destroy()
        view_books(tree)
        messagebox.showinfo("Thành công", "Đã thêm sách.")
        show_launch_app()  

    #tk.Button(top, text="Tự động điền từ Open Library", command=tu_dong_dien).pack(pady=10)
    tk.Button(top, text="Lưu", command=save).pack(pady=10)

# Xóa sách
def delete_book(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chọn sách", "Chọn sách cần xóa.")
        return
    item = tree.item(selected)
    book_id = item["values"][0]
    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sách ID {book_id}?"):
        return
    books = load_data(BOOKS_FILE)
    books = [b for b in books if b["id"] != book_id]
    save_data(BOOKS_FILE, books)
    view_books(tree)
    messagebox.showinfo("Thành công", "Đã xóa sách.")

# Sửa sách
def edit_book(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chọn sách", "Chọn sách cần sửa.")
        return
    item = tree.item(selected)
    book_id = item["values"][0]

    books = load_data(BOOKS_FILE)
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        messagebox.showerror("Lỗi", "Không tìm thấy sách.")
        return

    top = tk.Toplevel()
    top.title("Sửa sách")
    top.geometry("300x300")

    tk.Label(top, text="Tên sách").pack(pady=5)
    entry_title = tk.Entry(top)
    entry_title.insert(0, book["title"])
    entry_title.pack()

    tk.Label(top, text="Tác giả").pack(pady=5)
    entry_author = tk.Entry(top)
    entry_author.insert(0, book["author"])
    entry_author.pack()

    tk.Label(top, text="Năm").pack(pady=5)
    entry_year = tk.Entry(top)
    entry_year.insert(0, book["year"])
    entry_year.pack()

    tk.Label(top, text="Số lượng").pack(pady=5)
    entry_quantity = tk.Entry(top)
    entry_quantity.insert(0, str(book.get("quantity", 0)))
    entry_quantity.pack()
    def save_edit():
        # Lấy dữ liệu mới
        book["title"] = entry_title.get()
        book["author"] = entry_author.get()
        book["year"] = entry_year.get()
        try:
            book["quantity"] = int(entry_quantity.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên.")
            return
        save_data(BOOKS_FILE,books)
        tree.item(selected, values=(book["id"], book["title"], book["author"], book["year"], book["quantity"]))
        messagebox.showinfo("Thành công", "Sửa sách thành công.")
        top.destroy()
    tk.Button(top, text="Lưu", command=save_edit).pack(pady=10)

    
# Mượn sách
def borrow_book(tree, user):
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Thông báo", "Vui lòng chọn sách cần mượn.")
        return
    item = tree.item(selected)
    book_id, title, _, _, quantity = item["values"]
    if int(quantity) <= 0:
        messagebox.showwarning("Không thể mượn", "Sách đã hết.")
        return

    books = load_data(BOOKS_FILE)
    for b in books:
        if b["id"] == book_id:
            b["quantity"] = int(b["quantity"]) - 1
            break
    save_data(BOOKS_FILE, books)

    borrows = load_data(BORROW_FILE)
    borrows.append({
        "user": user,
        "book_id": book_id,
        "title": title,
        "date_borrow": datetime.date.today().isoformat()
    })
    save_data(BORROW_FILE, borrows)

    history = load_data(HISTORY_FILE)
    history.append({
        "user": user,
        "book_id": book_id,
        "title": title,
        "action": "Mượn",
        "date": datetime.date.today().isoformat()
    })
    save_data(HISTORY_FILE, history)

    messagebox.showinfo("Thành công", f"Đã mượn sách: {title}")
    view_books(tree)

# Trả sách
def return_book(tree, user):
    borrows = load_data(BORROW_FILE)
    user_books = [b for b in borrows if b["user"] == user]
    if not user_books:
        messagebox.showinfo("Thông báo", "Bạn chưa mượn sách nào.")
        return
    book_titles = [f"{b['book_id']} - {b['title']}" for b in user_books]
    choice = simpledialog.askstring("Trả sách", "Nhập ID sách cần trả:\n" + "\n".join(book_titles))
    if not choice:
        return
    book_to_return = next((b for b in user_books if b["book_id"] == choice), None)
    if not book_to_return:
        messagebox.showwarning("Lỗi", "ID sách không hợp lệ.")
        return
    borrows = [b for b in borrows if not (b["user"] == user and b["book_id"] == choice)]
    save_data(BORROW_FILE, borrows)
    books = load_data(BOOKS_FILE)
    for b in books:
        if b["id"] == choice:
            b["quantity"] = int(b.get("quantity", 0)) + 1
            break
    save_data(BOOKS_FILE, books)
    history = load_data(HISTORY_FILE)
    history.append({
        "user": user,
        "book_id": choice,
        "title": book_to_return["title"],
        "action": "Trả",
        "date": datetime.date.today().isoformat()
    })
    save_data(HISTORY_FILE, history)

    messagebox.showinfo("Thành công", "Đã trả sách.")
    view_books(tree)

# Tìm kiếm
def search_books(tree):
    keyword = simpledialog.askstring("Tìm kiếm", "Nhập tên sách, tác giả hoặc ID:")
    if not keyword:
        return
    books = load_data(BOOKS_FILE)
    result = [b for b in books if keyword.lower() in b["id"].lower() or
              keyword.lower() in b["title"].lower() or
              keyword.lower() in b["author"].lower()]
    tree.delete(*tree.get_children())
    for b in result:
        tree.insert("", "end", values=(b["id"], b["title"], b["author"], b["year"], b.get("quantity", 0)))

# In danh sách ra file
def print_books():
    books = load_data(BOOKS_FILE)
    with open("danhsach_sach.txt", "w", encoding="utf-8") as f:
        f.write("--- Danh sách Sách trong Thư viện ---\n")
        f.write("--------------------------------------------------\n")
        f.write(f"{'ID':<10} | {'Tên sách':<30} | {'Tác giả':<20} | {'Năm':<5} | {'Số lượng':<8}\n")
        f.write("--------------------------------------------------\n")
        for b in books:
            f.write(f"{b['id']:<10} | {b['title']:<30} | {b['author']:<20} | {b['year']:<5} | {b.get('quantity', 0):<8}\n")
    messagebox.showinfo("In danh sách", "Đã xuất file danhsach_sach.txt")

# Thống kê sách yêu thích
def thong_ke_sach_yeu_thich():
    history = load_data(HISTORY_FILE)
    count_dict = {}
    for entry in history:
        if entry["action"] == "Mượn":
            key = (entry["book_id"], entry["title"])
            count_dict[key] = count_dict.get(key, 0) + 1

    if not count_dict:
        messagebox.showinfo("Thống kê", "Chưa có dữ liệu mượn sách.")
        return

    sorted_books = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)

    top = tk.Toplevel()
    top.title("📊 Thống kê sách yêu thích")
    top.geometry("600x400")

    tk.Label(top, text="📚 TOP SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(top, columns=("STT", "ID", "Tên sách", "Số lượt mượn"), show="headings")
    tree.heading("STT", text="STT")
    tree.heading("ID", text="Mã sách")
    tree.heading("Tên sách", text="Tên sách")
    tree.heading("Số lượt mượn", text="Số lượt mượn")
    tree.column("STT", width=50)
    tree.column("ID", width=100)
    tree.column("Tên sách", width=300)
    tree.column("Số lượt mượn", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for idx, ((book_id, title), count) in enumerate(sorted_books, start=1):
        tree.insert("", "end", values=(idx, book_id, title, count))
def search_borrowers():
    keyword = simpledialog.askstring("Tìm kiếm người dùng", "Nhập tên người dùng hoặc ID sách:")
    if not keyword:
        return
    borrows = load_data(BORROW_FILE)
    result = [b for b in borrows if keyword.lower() in b["user"].lower() or keyword.lower() in b["book_id"].lower()]
    if not result:
        messagebox.showinfo("Kết quả", "Không tìm thấy người dùng hoặc sách tương ứng.")
        return

    top = tk.Toplevel()
    top.title("Kết quả tìm kiếm người dùng mượn sách")
    top.geometry("700x400")

    tree = ttk.Treeview(top, columns=("Người dùng", "Mã sách", "Tên sách", "Ngày mượn"), show="headings")
    tree.heading("Người dùng", text="Người dùng")
    tree.heading("Mã sách", text="Mã sách")
    tree.heading("Tên sách", text="Tên sách")
    tree.heading("Ngày mượn", text="Ngày mượn")
    tree.column("Người dùng", width=150)
    tree.column("Mã sách", width=100)
    tree.column("Tên sách", width=300)
    tree.column("Ngày mượn", width=100)
    tree.pack(fill="both", expand=True)

    for b in result:
        tree.insert("", "end", values=(b["user"], b["book_id"], b["title"], b["date_borrow"]))
def thong_ke_lich_su_muon_tra():
    history = load_data(HISTORY_FILE)
    if not history:
        messagebox.showinfo("Thống kê", "Chưa có dữ liệu lịch sử mượn trả.")
        return

    top = tk.Toplevel()
    top.title("📊 Thống kê lịch sử mượn trả sách")
    top.geometry("800x450")

    tk.Label(top, text="📚 Lịch sử mượn trả sách chi tiết", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(top, columns=("Người dùng", "Mã sách", "Tên sách", "Hành động", "Ngày"), show="headings")
    tree.heading("Người dùng", text="Người dùng")
    tree.heading("Mã sách", text="Mã sách")
    tree.heading("Tên sách", text="Tên sách")
    tree.heading("Hành động", text="Hành động")
    tree.heading("Ngày", text="Ngày")
    tree.column("Người dùng", width=150)
    tree.column("Mã sách", width=100)
    tree.column("Tên sách", width=300)
    tree.column("Hành động", width=80)
    tree.column("Ngày", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for entry in history:
        tree.insert("", "end", values=(
            entry["user"],
            entry["book_id"],
            entry["title"],
            entry["action"],
            entry["date"]
        ))

def logout(root):
    if messagebox.askyesno("Đăng xuất", "Bạn có muốn đăng xuất?"):
        root.destroy()
        return False
      


# Giao diện chính
def launch_app(username, role):
    root = tk.Tk()
    root.title(f"📚 QUẢN LÝ THƯ VIỆN - {username} ({role})")
    root.geometry("800x500")
    root.configure(bg="#eef6ff")

    title = tk.Label(root, text="HỆ THỐNG QUẢN LÝ THƯ VIỆN", font=("Arial", 16, "bold"), bg="#eef6ff", fg="#0055aa")
    title.pack(pady=10)

    tree = ttk.Treeview(root, columns=("ID", "Tên", "Tác giả", "Năm", "Số lượng"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(padx=10, pady=5, fill="both", expand=True)
    view_books(tree)

    frame = tk.Frame(root, bg="#eef6ff")
    frame.pack(pady=10)

    if role == "user":
        tk.Button(frame, text="🔍 Tìm kiếm", command=lambda: search_books(tree)).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="📘 Mượn sách", command=lambda: borrow_book(tree, username)).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="📕 Trả sách", command=lambda: return_book(tree, username)).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="📊 Thống kê", command=thong_ke_sach_yeu_thich).grid(row=0, column=3, padx=5)
    
    
    elif role == "admin":
        tk.Button(frame, text="➕ Thêm", command=lambda: add_book(tree)).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="✏️ Sửa", command=lambda: edit_book(tree)).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="🗑️ Xóa", command=lambda: delete_book(tree)).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="🖨️ In DS", command=print_books).grid(row=0, column=3, padx=5)
        tk.Button(frame, text="📊 Thống kê", command=thong_ke_sach_yeu_thich).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="🔍 Tìm kiếm", command=lambda: search_books(tree)).grid(row=0, column=5, padx=5)
        tk.Button(frame, text="🔍 Tìm người dùng mượn", command=search_borrowers).grid(row=0, column=6, padx=5)
        tk.Button(frame, text="📋 Lịch sử mượn trả", command=thong_ke_lich_su_muon_tra).grid(row=0, column=7, padx=5)
        btn_ql_user = tk.Button(frame, text="Quản lý người dùng", command=quan_ly_nguoi_dung)
        btn_ql_user.grid(pady=10)

    tk.Button(root, text="🔒 Đăng xuất", font=("Arial", 12, "bold"), fg="red",
              command=lambda: logout(root)).pack(pady=20)
    root.mainloop()
if __name__ == "__main__":
    result = show_login_window()
    if result:
        username, role = result
        launch_app(username, role)
        
