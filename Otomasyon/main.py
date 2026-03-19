import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv

# Opsiyonel kütüphaneler
try:
    import pandas as pd
except Exception:
    pd = None

try:
    from pandastable import Table
except Exception:
    Table = None

import database as db

# --- Yardımcılar ---
def center(win):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def enable_widgets(widgets, state="normal"):
    for w in widgets:
        try:
            w.configure(state=state)
        except Exception:
            pass

# --- Giriş Ekranı ---
def show_login(root):
    login = tk.Toplevel(root)
    login.title("Giriş")
    login.geometry("360x280")
    login.resizable(False, False)

    frm = ttk.Frame(login, padding=16)
    frm.pack(expand=True, fill="both")

    ttk.Label(frm, text="Kullanıcı Adı:").grid(row=0, column=0, sticky="w", pady=4)
    ent_user = ttk.Entry(frm, width=24)
    ent_user.grid(row=0, column=1, sticky="ew", pady=4)

    ttk.Label(frm, text="Şifre:").grid(row=1, column=0, sticky="w", pady=4)
    ent_pass = ttk.Entry(frm, show="*", width=24)
    ent_pass.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frm, text="Rol:").grid(row=2, column=0, sticky="w", pady=4)
    role_var = tk.StringVar(value="ogrenci")
    cmb_role = ttk.Combobox(frm, textvariable=role_var, values=["admin","ogretmen","ogrenci"], state="readonly", width=22)
    cmb_role.grid(row=2, column=1, sticky="ew", pady=4)

    keep_var = tk.BooleanVar(value=True)
    chk = ttk.Checkbutton(frm, text="Beni hatırla (demoda etkisiz)", variable=keep_var)
    chk.grid(row=3, column=1, sticky="w")

    def do_login():
        u = ent_user.get().strip()
        p = ent_pass.get().strip()
        res = db.authenticate(u,p)
        if not res:
            messagebox.showerror("Hata","Kullanıcı adı / şifre hatalı.")
            return
        if cmb_role.get() != res["role"]:
            messagebox.showwarning("Uyarı","Seçtiğiniz rol ile hesabın rolü uyuşmuyor. Hesabın rolü: " + res["role"])
        login.destroy()
        init_main_ui(root, u, res["role"], res["user_id"])

    btn = ttk.Button(frm, text="Giriş Yap", command=do_login)
    btn.grid(row=4, column=0, columnspan=2, pady=12, sticky="ew")

    frm.columnconfigure(1, weight=1)
    center(login)

# --- Ana UI ---
def init_main_ui(root, username, role, user_id):
    for child in root.winfo_children():
        child.destroy()

    root.title(f"Öğrenci Otomasyon - Giriş yapan: {username} ({role})")
    wrapper = ttk.Frame(root, padding=10)
    wrapper.pack(fill="both", expand=True)

    # Üst menü
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Dosya", menu=file_menu)
    file_menu.add_command(label="Excel'e Aktar (Notlar)", command=lambda: export_grades_excel(user_id, role))
    file_menu.add_separator()
    file_menu.add_command(label="Çıkış", command=root.destroy)

    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Görünüm", menu=view_menu)
    view_menu.add_command(label="Notları Tablo Olarak Aç", command=lambda: show_grades_table(user_id, role))

    # Sol panel: Öğrenci & Ders listeleri
    left = ttk.LabelFrame(wrapper, text="Listeler", padding=8)
    left.pack(side="left", fill="y")

    ttk.Label(left, text="Öğrenciler").pack(anchor="w")
    lst_students = tk.Listbox(left, height=10)
    lst_students.pack(fill="x", pady=(0,6))

    ttk.Label(left, text="Dersler").pack(anchor="w")
    lst_courses = tk.Listbox(left, height=10)
    lst_courses.pack(fill="x", pady=(0,6))

    # Orta panel: İşlemler
    center_fr = ttk.LabelFrame(wrapper, text="İşlemler", padding=8)
    center_fr.pack(side="left", fill="both", expand=True, padx=8)

    # Öğrenci ekleme
    ttk.Label(center_fr, text="Öğrenci No").grid(row=0, column=0, sticky="e", pady=2)
    ent_sno = ttk.Entry(center_fr, width=14); ent_sno.grid(row=0, column=1, sticky="w")
    ttk.Label(center_fr, text="Ad").grid(row=1, column=0, sticky="e", pady=2)
    ent_sfn = ttk.Entry(center_fr, width=14); ent_sfn.grid(row=1, column=1, sticky="w")
    ttk.Label(center_fr, text="Soyad").grid(row=2, column=0, sticky="e", pady=2)
    ent_sln = ttk.Entry(center_fr, width=14); ent_sln.grid(row=2, column=1, sticky="w")
    ttk.Label(center_fr, text="E-posta").grid(row=3, column=0, sticky="e", pady=2)
    ent_sem = ttk.Entry(center_fr, width=18); ent_sem.grid(row=3, column=1, sticky="w")

    # Ders ekleme
    ttk.Separator(center_fr, orient="horizontal").grid(row=4, column=0, columnspan=4, sticky="ew", pady=6)
    ttk.Label(center_fr, text="Ders Kodu").grid(row=5, column=0, sticky="e", pady=2)
    ent_cc = ttk.Entry(center_fr, width=14); ent_cc.grid(row=5, column=1, sticky="w")
    ttk.Label(center_fr, text="Ders Adı").grid(row=6, column=0, sticky="e", pady=2)
    ent_cn = ttk.Entry(center_fr, width=18); ent_cn.grid(row=6, column=1, sticky="w")
    ttk.Label(center_fr, text="Kredi").grid(row=7, column=0, sticky="e", pady=2)
    cmb_credit = ttk.Combobox(center_fr, values=[2,3,4,5,6], width=12, state="readonly")
    cmb_credit.set(3); cmb_credit.grid(row=7, column=1, sticky="w")

    # Not girişi
    ttk.Separator(center_fr, orient="horizontal").grid(row=8, column=0, columnspan=4, sticky="ew", pady=6)
    ttk.Label(center_fr, text="Not Girişi").grid(row=9, column=0, sticky="e")
    ent_grade = ttk.Entry(center_fr, width=8); ent_grade.grid(row=9, column=1, sticky="w")
    ttk.Label(center_fr, text="Seçim: Öğrenci + Ders listeden").grid(row=9, column=2, sticky="w")

    # Sağ panel: Hızlı işlemler
    right = ttk.LabelFrame(wrapper, text="Hızlı İşlemler", padding=8)
    right.pack(side="left", fill="y")

    enroll_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(right, text="Kayıt (enroll) işlevini aktif tut", variable=enroll_var).pack(anchor="w")
    mode_var = tk.StringVar(value="ekle")
    ttk.Radiobutton(right, text="Ekle Modu", variable=mode_var, value="ekle").pack(anchor="w")
    ttk.Radiobutton(right, text="Sil Modu", variable=mode_var, value="sil").pack(anchor="w")

    # Butonlar
    def refresh_lists():
        lst_students.delete(0, tk.END)
        for s in db.list_students():
            lst_students.insert(tk.END, f"{s[0]} | {s[1]} | {s[2]} {s[3]}")

        lst_courses.delete(0, tk.END)
        for c in db.list_courses():
            lst_courses.insert(tk.END, f"{c[0]} | {c[1]} | {c[2]} (kredi:{c[3]})")

    def add_student_ui():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen öğrenci ekleyebilir.")
            return
        try:
            db.add_student(ent_sno.get(), ent_sfn.get(), ent_sln.get(), ent_sem.get())
            refresh_lists()
            messagebox.showinfo("Tamam","Öğrenci eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def add_course_ui():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen ders ekleyebilir.")
            return
        try:
            db.add_course(ent_cc.get(), ent_cn.get(), int(cmb_credit.get()))
            refresh_lists()
            messagebox.showinfo("Tamam","Ders eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def delete_selected_student():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen silebilir.")
            return
        sel = lst_students.curselection()
        if not sel: return
        sid = int(lst_students.get(sel[0]).split("|")[0].strip())
        db.delete_student(sid)
        refresh_lists()

    def delete_selected_course():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen silebilir.")
            return
        sel = lst_courses.curselection()
        if not sel: return
        cid = int(lst_courses.get(sel[0]).split("|")[0].strip())
        db.delete_course(cid)
        refresh_lists()

    def enroll_selected():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen kayıt yapabilir.")
            return
        ssel = lst_students.curselection()
        csel = lst_courses.curselection()
        if not ssel or not csel:
            messagebox.showwarning("Uyarı","Öğrenci ve ders seçiniz.")
            return
        sid = int(lst_students.get(ssel[0]).split("|")[0].strip())
        cid = int(lst_courses.get(csel[0]).split("|")[0].strip())
        db.enroll_student(sid, cid)
        messagebox.showinfo("Tamam","Kayıt yapıldı.")

    def add_grade_ui():
        if role not in ("admin","ogretmen"):
            messagebox.showwarning("Yetki","Sadece admin/öğretmen not girebilir.")
            return
        try:
            ssel = lst_students.curselection()
            csel = lst_courses.curselection()
            if not ssel or not csel:
                messagebox.showwarning("Uyarı","Öğrenci ve ders seçiniz.")
                return
            sid = int(lst_students.get(ssel[0]).split("|")[0].strip())
            cid = int(lst_courses.get(csel[0]).split("|")[0].strip())
            g = float(ent_grade.get())
            db.add_grade(sid, cid, g)
            messagebox.showinfo("Tamam","Not kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    # Raporlar
    def get_grades_df():
        rows = db.list_grades(student_id=user_id if role=="ogrenci" else None)
        cols = ["grade_id","ogr_no","ad_soyad","ders_kodu","ders_adi","not"]
        if pd is not None:
            return pd.DataFrame(rows, columns=cols)
        # pandas yoksa CSV benzeri yapı döndür
        return rows, cols

    def export_grades_excel(user_id, role):
        if pd is None:
            messagebox.showinfo("Bilgi","Pandas kurulu değil. `pip install pandas` ile kurup tekrar deneyin.")
            return
        df = get_grades_df()
        if isinstance(df, tuple):  # güvenlik
            messagebox.showerror("Hata","Veri çerçevesi oluşturulamadı.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not path: return
        df.to_excel(path, index=False)
        messagebox.showinfo("Tamam", f"Excel'e aktarıldı:\n{path}")

    def show_grades_table(user_id, role):
        df = get_grades_df()
        if isinstance(df, tuple):
            # pandas yoksa basit pencerede listele
            rows, cols = df
            top = tk.Toplevel(root)
            top.title("Notlar (Basit Görünüm)")
            tree = ttk.Treeview(top, columns=cols, show="headings")
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=120, stretch=True)
            for r in rows:
                tree.insert("", "end", values=r)
            tree.pack(fill="both", expand=True)
            center(top)
            return

        if Table is None:
            messagebox.showinfo("Bilgi","pandastable kurulu değil. `pip install pandastable` ile kurup tekrar deneyin.")
            return
        top = tk.Toplevel(root)
        top.title("Notlar (pandastable)")
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True)
        pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
        pt.show()
        center(top)

    # Buton yerleşimleri
    btns = ttk.Frame(right)
    btns.pack(fill="x", pady=6)
    ttk.Button(btns, text="Öğrenci Ekle", command=add_student_ui).pack(fill="x", pady=2)
    ttk.Button(btns, text="Öğrenci Sil (seçili)", command=delete_selected_student).pack(fill="x", pady=2)
    ttk.Button(btns, text="Ders Ekle", command=add_course_ui).pack(fill="x", pady=2)
    ttk.Button(btns, text="Ders Sil (seçili)", command=delete_selected_course).pack(fill="x", pady=2)
    ttk.Button(btns, text="Öğrenciyi Derse Yaz", command=enroll_selected).pack(fill="x", pady=2)
    ttk.Button(btns, text="Not Kaydet", command=add_grade_ui).pack(fill="x", pady=2)
    ttk.Button(btns, text="Notları Göster", command=lambda: show_grades_table(user_id, role)).pack(fill="x", pady=2)

    # Rol sınırlamaları
    if role == "ogrenci":
        # öğrencide CRUD devre dışı
        disable = [ent_sno, ent_sfn, ent_sln, ent_sem, ent_cc, ent_cn, cmb_credit, ent_grade]
        enable_widgets(disable, state="disabled")

    # başlangıç yüklemeleri
    refresh_lists()

    # Alt durum çubuğu
    status = ttk.Label(root, text="Hazır", anchor="w")
    status.pack(side="bottom", fill="x")

def main():
    # veritabanı hazır mı?
    db.create_tables()
    db.seed_demo_data()

    root = tk.Tk()
    root.title("Öğrenci Otomasyon - Giriş")
    root.geometry("900x520")
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Ana ekranda sadece "Giriş" tuşu göster
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True)
    ttk.Label(frame, text="Öğrenci Otomasyon (Tkinter + SQLite)", font=("Segoe UI", 14, "bold")).pack(pady=6)
    ttk.Button(frame, text="Giriş Yap", command=lambda: show_login(root)).pack(pady=10)
    ttk.Label(frame, text="Roller: admin/ogretmen/ogrenci (örnek kullanıcılar mevcuttur)").pack()

    center(root)
    root.mainloop()

if __name__ == "__main__":
    main()
