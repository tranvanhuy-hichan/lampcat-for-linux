#!/usr/bin/env python3
"""Control panel for the local web stack (Apache + PHP, MariaDB, Tomcat, phpMyAdmin).

Everything lives under the project folder and runs as the current user, so no sudo
or password prompts are needed. Services are started/stopped through ../lampcat.sh.
"""
import os
import re
import shutil
import socket
import subprocess
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from tkinter import filedialog, messagebox, ttk

# Window/taskbar icon (packaging/lampcat.svg rendered at 128px). Embedded so it also works when the
# panel is started from a checkout, without the installed .desktop file.
ICON_PNG = (
    "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"
)

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LAMPCAT_SH = os.path.join(ROOT, "lampcat.sh")


def p(*parts):
    return os.path.join(ROOT, *parts)


# Every pattern has groups pre, port, post (post may be empty).
_PORT_EQ = r"(?P<pre>^[ \t]*port[ \t]*=[ \t]*)(?P<port>\d+)(?P<post>[ \t]*$)"
SERVICES = {
    "Apache": dict(
        key="apache", pid=p("apache", "run", "httpd.pid"), default=8000,
        conf=p("apache", "conf", "httpd.conf"), log=p("apache", "logs", "error.log"),
        patterns=[r"(?P<pre>^Listen[ \t]+)(?P<port>\d+)(?P<post>[ \t]*$)",
                  r"(?P<pre>^ServerName[ \t]+[^\s:]+:)(?P<port>\d+)(?P<post>[ \t]*$)"],
    ),
    "MySQL": dict(
        key="mysql", pid=p("mysql", "run", "mysqld.pid"), default=3307,
        conf=p("mysql", "my.cnf"), log=p("mysql", "logs", "error.log"),
        patterns=[_PORT_EQ],
    ),
    "Tomcat": dict(
        key="tomcat", pid=p("tomcat", "temp", "catalina.pid"), default=8080,
        conf=p("tomcat", "conf", "server.xml"), log=p("tomcat", "logs", "catalina.out"),
        patterns=[r'(?P<pre><Connector\s+port=")(?P<port>\d+)(?P<post>"\s+protocol="HTTP/1\.1")'],
    ),
}


# ---------------------------------------------------------------- helpers
def pid_alive(path):
    try:
        pid = int(open(path).read().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", int(port)), 0.3):
            return True
    except OSError:
        return False


def get_port(name):
    s = SERVICES[name]
    try:
        text = open(s["conf"], encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = re.search(s["patterns"][0], text, re.M | re.S)
    return int(m.group("port")) if m else s["default"]


def set_port(name, port):
    """Rewrite the port in the service's config (keeps a .bak). Returns replacements made."""
    s = SERVICES[name]
    text = open(s["conf"], encoding="utf-8").read()
    total = 0
    for pat in s["patterns"]:
        text, n = re.subn(pat, lambda m: m.group("pre") + str(port) + m.group("post"),
                          text, flags=re.M | re.S)
        total += n
    if total == 0:
        raise RuntimeError("Không tìm thấy dòng port trong " + s["conf"])
    if not os.path.exists(s["conf"] + ".bak"):
        shutil.copy2(s["conf"], s["conf"] + ".bak")
    with open(s["conf"], "w", encoding="utf-8") as f:
        f.write(text)
    return total


CONFIG_ENV = p("config.env")


def get_web_root():
    """Absolute path of the shared web root (WEB_ROOT in config.env, default www)."""
    val = "www"
    try:
        for line in open(CONFIG_ENV, encoding="utf-8"):
            if line.startswith("WEB_ROOT="):
                val = line.split("=", 1)[1].strip().strip('"') or val
    except OSError:
        pass
    return val if os.path.isabs(val) else os.path.normpath(os.path.join(ROOT, val))


def set_web_root(path):
    path = os.path.abspath(path)
    rel = os.path.relpath(path, ROOT)
    val = rel if not rel.startswith("..") else path  # keep it relocatable when inside the project
    with open(CONFIG_ENV, "w", encoding="utf-8") as f:
        f.write("# Shared web root for Apache (PHP) and Tomcat (JSP/Servlet)\nWEB_ROOT=%s\n" % val)


COLORS = {  # name: (normal, hover)
    "green": ("#1a7f37", "#15692e"), "red": ("#cf222e", "#a40e26"),
    "blue": ("#0969da", "#0757b8"), "slate": ("#57606a", "#424a53"),
    "orange": ("#d9640a", "#b85208"), "grey": ("#9aa0a6", "#9aa0a6"),
}


def cbtn(parent, text, color, command, width=None):
    """Flat coloured button (ttk buttons can't be recoloured on every theme)."""
    bg, hover = COLORS[color]
    return tk.Button(parent, text=text, command=command, width=width, bg=bg, fg="white",
                     activebackground=hover, activeforeground="white", disabledforeground="#f0f0f0",
                     relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
                     font=("TkDefaultFont", 9, "bold"))


def recolor(btn, color, text=None):
    bg, hover = COLORS[color]
    btn.config(bg=bg, activebackground=hover)
    if text is not None:
        btn.config(text=text)


PROJECTS_FILE = p("projects.conf")


def slugify(text):
    return re.sub(r"[^a-z0-9_-]+", "-", text.lower()).strip("-")


def load_projects():
    """[(name, folder), ...] from projects.conf (tab separated)."""
    out = []
    try:
        for line in open(PROJECTS_FILE, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.strip() and not line.lstrip().startswith("#") and "\t" in line:
                name, folder = line.split("\t", 1)
                out.append((name, folder))
    except OSError:
        pass
    return out


def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        f.write("# name<TAB>folder - managed by the control panel (Projects tab)\n")
        for name, folder in projects:
            f.write(f"{name}\t{folder}\n")


def pick_folder(win, title, initial):
    """Native folder dialog (zenity/kdialog) so it looks and behaves like the rest of the desktop;
    falls back to Tk's own chooser. Returns a path or "" if cancelled."""
    initial = initial if os.path.isdir(initial) else os.path.expanduser("~")
    cmd = None
    if shutil.which("zenity"):
        cmd = ["zenity", "--file-selection", "--directory", "--title=" + title,
               "--filename=" + initial.rstrip("/") + "/"]
    elif shutil.which("kdialog"):
        cmd = ["kdialog", "--getexistingdirectory", initial, "--title", title]
    if cmd:
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            while proc.poll() is None:  # keep the panel repainting while the dialog is open
                win.update()
                time.sleep(0.03)
            return proc.stdout.read().strip() if proc.returncode == 0 else ""
        except OSError:
            pass
    return filedialog.askdirectory(title=title, initialdir=initial, mustexist=True) or ""


def open_path(path):
    if os.path.exists(path):
        subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        messagebox.showinfo("Không tìm thấy", path + "\nchưa tồn tại.")


# -------------------------------------------------------------------- GUI
class Panel(tk.Tk):
    def __init__(self):
        # className becomes WM_CLASS: it must match StartupWMClass in lampcat.desktop for the dock to
        # attach the window to the launcher (and show its icon) instead of "Lampcat-panel.py".
        super().__init__(className="Lampcat")
        self.title("Lampcat Control Panel")
        try:
            self._icon = tk.PhotoImage(data=ICON_PNG)
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass
        self.rows = {}

        st = ttk.Style(self)
        # row height must follow the font: a fixed number clips the text on large/HiDPI fonts
        st.configure("Treeview", rowheight=tkfont.nametofont("TkDefaultFont").metrics("linespace") + 8)
        st.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))

        head = ttk.Frame(self)
        head.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Label(head, text="Lampcat Control Panel",
                  font=("TkDefaultFont", 14, "bold")).pack(side="left")
        tabbar = ttk.Frame(head)
        tabbar.pack(side="right")
        self.tab_btns = {}
        for key, text in (("services", "Dịch vụ"), ("projects", "Dự án")):
            btn = tk.Button(tabbar, text=text, relief="flat", bd=0, padx=16, pady=5, cursor="hand2",
                            font=("TkDefaultFont", 9, "bold"), command=lambda k=key: self.show_tab(k))
            btn.pack(side="left", padx=(4, 0))
            self.tab_btns[key] = btn
        ttk.Label(self, text=ROOT, foreground="#666").pack(anchor="w", padx=12)
        ttk.Separator(self).pack(fill="x", padx=12, pady=(6, 0))

        # both tabs share one grid cell, so the window is as tall as the taller one
        content = ttk.Frame(self)
        content.pack(fill="x", padx=12)
        content.columnconfigure(0, weight=1)
        tab_services = ttk.Frame(content)
        tab_projects = ttk.Frame(content)
        for f in (tab_services, tab_projects):
            f.grid(row=0, column=0, sticky="nsew")
        self.tabs = {"services": tab_services, "projects": tab_projects}

        grid = ttk.Frame(tab_services)
        grid.pack(fill="x", padx=8, pady=10)
        heads = ["Service", "Status", "Port", "", "Action", "", "", ""]
        for i, h in enumerate(heads):
            ttk.Label(grid, text=h, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=i, padx=5, sticky="w")
        for r, name in enumerate(SERVICES, start=1):
            self._build_row(grid, r, name)

        rootbar = ttk.Frame(tab_services)
        rootbar.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(rootbar, text="Web root:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.root_var = tk.StringVar(value=get_web_root())
        ttk.Entry(rootbar, textvariable=self.root_var, state="readonly").pack(
            side="left", fill="x", expand=True, padx=6)
        cbtn(rootbar, "Change...", "slate", self.change_root).pack(side="left")
        cbtn(rootbar, "Open folder", "slate",
             lambda: open_path(get_web_root())).pack(side="left", padx=(6, 0))

        self._build_projects_tab(tab_projects)
        self.show_tab("services")

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=12, pady=(8, 0))
        cbtn(bar, "Start All", "green", lambda: self.all("start")).pack(side="left")
        cbtn(bar, "Stop All", "red", lambda: self.all("stop")).pack(side="left", padx=6)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        cbtn(bar, "php.ini", "slate", lambda: open_path(p("php", "php.ini"))).pack(side="left", padx=6)
        cbtn(bar, "Clear log", "slate", lambda: self.log_w.delete("1.0", "end")).pack(side="right")

        self.log_w = tk.Text(self, height=9, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#fff")
        self.log_w.pack(fill="both", expand=True, padx=12, pady=10)
        self.log("Sẵn sàng. Đặt code (PHP, JSP, servlet) vào Web root: Apache chạy PHP, Tomcat chạy JSP/servlet.")
        self.poll()
        self.fit_to_content()

    def show_tab(self, key):
        self.tabs[key].tkraise()
        for k, btn in self.tab_btns.items():
            on = k == key
            btn.config(bg="#24292f" if on else "#d0d7de", fg="#ffffff" if on else "#24292f",
                       activebackground="#24292f" if on else "#b8c0c8",
                       activeforeground="#ffffff" if on else "#24292f")

    def fit_to_content(self):
        """Size the window to its content (so nothing is cut off) and centre it."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = min(self.winfo_reqwidth(), sw - 40)
        h = min(max(self.winfo_reqheight(), 440), sh - 100)
        self.minsize(w, 360)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 3}")

    def _build_row(self, grid, r, name):
        s = SERVICES[name]
        row = dict(port=get_port(name), busy=False)
        ttk.Label(grid, text=name, width=9).grid(row=r, column=0, padx=5, pady=4, sticky="w")
        row["status"] = tk.Label(grid, text="...", width=11, font=("TkDefaultFont", 9, "bold"), pady=2)
        row["status"].grid(row=r, column=1, padx=5, sticky="w")
        row["var"] = tk.StringVar(value=str(row["port"] or ""))
        ttk.Entry(grid, textvariable=row["var"], width=7).grid(row=r, column=2, padx=5)
        cbtn(grid, "Save port", "orange", lambda n=name: self.save_port(n), 9).grid(row=r, column=3, padx=5)
        row["btn"] = cbtn(grid, "Start", "green", lambda n=name: self.toggle(n), 7)
        row["btn"].grid(row=r, column=4, padx=5)
        cbtn(grid, "Open", "blue", lambda n=name: self.open_web(n), 6).grid(row=r, column=5, padx=3)
        cbtn(grid, "Config", "slate", lambda c=s["conf"]: open_path(c), 7).grid(row=r, column=6, padx=3)
        cbtn(grid, "Logs", "slate", lambda l=s["log"]: open_path(l), 6).grid(row=r, column=7, padx=3)
        self.rows[name] = row

    # ---- logging / status
    def log(self, msg):
        self.log_w.insert("end", time.strftime("[%H:%M:%S] ") + msg + "\n")
        self.log_w.see("end")

    def tlog(self, msg):  # thread-safe
        self.after(0, self.log, msg)

    def running(self, name):
        return pid_alive(SERVICES[name]["pid"])

    def poll(self):
        for name, row in self.rows.items():
            up = self.running(name)
            if row["busy"]:
                row["status"].config(text="◌ Working…", bg="#fff4cc", fg="#8a5a00")
            elif up:
                row["status"].config(text="● Running", bg="#1a7f37", fg="#ffffff")
            else:
                row["status"].config(text="○ Stopped", bg="#ffe0e0", fg="#b42318")
            if not row["busy"]:
                recolor(row["btn"], "red" if up else "green", "Stop" if up else "Start")
        self.after(1500, self.poll)

    # ---- actions
    def run_async(self, name, fn):
        row = self.rows[name]
        if row["busy"]:
            return
        row["busy"] = True
        row["btn"].config(state="disabled", bg=COLORS["grey"][0])

        def work():
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                self.tlog(f"[{name}] LỖI: {e}")
            finally:
                def done():
                    row["busy"] = False
                    row["btn"].config(state="normal")
                self.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def _exec(self, name, action):
        r = subprocess.run([LAMPCAT_SH, SERVICES[name]["key"], action],
                           capture_output=True, text=True, timeout=180)
        for line in (r.stdout + r.stderr).strip().splitlines():
            self.tlog(f"[{name}] {line}")
        if r.returncode != 0:
            raise RuntimeError(f"{action} thất bại (exit {r.returncode})")

    def toggle(self, name):
        if self.running(name):
            self.run_async(name, lambda: self._exec(name, "stop"))
            return
        port = self.rows[name]["port"]
        if port and port_open(port):
            messagebox.showerror("Port đang bị chiếm",
                                 f"Port {port} đang được chương trình khác dùng.\n"
                                 "Đổi sang port khác (Save port) rồi Start lại.")
            return
        self.run_async(name, lambda: self._exec(name, "start"))

    def all(self, action):
        for name in self.rows:
            up = self.running(name)
            if action == "start" and not up:
                self.toggle(name)
            elif action == "stop" and up:
                self.toggle(name)

    def save_port(self, name):
        row = self.rows[name]
        try:
            new = int(row["var"].get())
            if not 1024 <= new <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Port không hợp lệ",
                                 "Port phải từ 1024 đến 65535 (dưới 1024 cần quyền root).")
            return
        old = row["port"]
        if new == old:
            return
        was_up = self.running(name)
        if port_open(new) and not (was_up and new == old):
            if not messagebox.askyesno("Port đang bị chiếm",
                                       f"Port {new} đang được chương trình khác dùng. Vẫn lưu?"):
                return
        restart = was_up and messagebox.askyesno(
            "Khởi động lại?", f"{name} đang chạy. Lưu port {new} và khởi động lại ngay?")

        def work():
            n = set_port(name, new)
            row["port"] = new
            self.after(0, self.refresh_projects)
            self.tlog(f"[{name}] port {old} -> {new} (sửa {n} dòng, có file .bak)")
            if restart:
                self._exec(name, "restart")
            elif was_up:
                self.tlog(f"[{name}] cần Stop/Start để dùng port mới")
        self.run_async(name, work)

    def change_root(self):
        new = pick_folder(self, "Chọn thư mục gốc (web root)", get_web_root())
        if not new or os.path.abspath(new) == get_web_root():
            return
        set_web_root(new)
        self.root_var.set(get_web_root())
        self.log(f"Web root -> {get_web_root()}")
        running = [n for n in ("Apache", "Tomcat") if self.running(n)]
        if running and messagebox.askyesno(
                "Khởi động lại?", f"{' và '.join(running)} đang chạy. Khởi động lại để dùng thư mục mới?"):
            for n in running:
                self.run_async(n, lambda n=n: self._exec(n, "restart"))
        elif running:
            self.log("Cần Stop/Start Apache và Tomcat để dùng web root mới.")

    # ---- projects tab
    def _build_projects_tab(self, tab):
        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, padx=8, pady=(10, 6))
        self.tree = ttk.Treeview(body, columns=("name", "folder", "php", "jsp"), show="headings",
                                 height=4, selectmode="browse")
        for col, text, w in (("name", "Tên", 90), ("folder", "Thư mục", 240),
                             ("php", "PHP (Apache)", 210), ("jsp", "JSP (Tomcat)", 200)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="w", stretch=(col == "folder"))
        sb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.open_project("php"))
        btns = ttk.Frame(tab)
        btns.pack(fill="x", padx=8, pady=(0, 10))
        cbtn(btns, "+ Thêm dự án", "green", self.add_project).pack(side="left")
        cbtn(btns, "Xoá", "red", self.remove_project).pack(side="left", padx=6)
        ttk.Separator(btns, orient="vertical").pack(side="left", fill="y", padx=6)
        cbtn(btns, "Mở PHP", "blue", lambda: self.open_project("php")).pack(side="left")
        cbtn(btns, "Mở JSP", "blue", lambda: self.open_project("jsp")).pack(side="left", padx=6)
        cbtn(btns, "Mở thư mục", "slate", self.open_project_folder).pack(side="left")
        self.refresh_projects()

    def _project_urls(self, name):
        ap = self.rows["Apache"]["port"] or 8000
        tp = self.rows["Tomcat"]["port"] or 8080
        return f"http://{name}.localhost:{ap}/", f"http://localhost:{tp}/{name}/"

    def refresh_projects(self):
        home = os.path.expanduser("~")
        self.tree.delete(*self.tree.get_children())
        data = []
        for name, folder in load_projects():
            php, jsp = self._project_urls(name)
            short = "~" + folder[len(home):] if folder.startswith(home + os.sep) else folder
            data.append((name, short, php[7:], jsp[7:]))  # no "http://": it is just noise here
            self.tree.insert("", "end", iid=name, values=data[-1])
        # size every column from the real text width (fonts scale, fixed pixel widths do not)
        fnt = tkfont.nametofont("TkDefaultFont")
        heads = {"name": "Tên", "folder": "Thư mục", "php": "PHP (Apache)", "jsp": "JSP (Tomcat)"}
        for i, col in enumerate(("name", "folder", "php", "jsp")):
            w = max([fnt.measure(heads[col])] + [fnt.measure(r[i]) for r in data]) + 28
            self.tree.column(col, width=w, minwidth=w if col != "folder" else 120,
                             stretch=(col == "folder"))
        self.update_idletasks()
        need = self.winfo_reqwidth()
        if self.winfo_width() > 1 and need > self.winfo_width():  # grow the window, never clip
            self.geometry(f"{need}x{self.winfo_height()}")

    def _selected_project(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Chọn một dự án trong danh sách trước.")
            return None
        folder = dict(load_projects()).get(sel[0])
        return (sel[0], folder) if folder else None

    def apply_projects(self):
        """Regenerate the Apache/Tomcat project config and reload what is running."""
        def work():
            r = subprocess.run([LAMPCAT_SH, "projects", "sync"], capture_output=True, text=True, timeout=60)
            for line in (r.stdout + r.stderr).strip().splitlines():
                self.tlog(f"[Dự án] {line}")
        threading.Thread(target=work, daemon=True).start()

    def add_project(self):
        folder = pick_folder(self, "Chọn thư mục dự án", os.path.dirname(get_web_root()))
        if not folder:
            return
        folder = os.path.abspath(folder)
        if '"' in folder or "\t" in folder:
            messagebox.showerror("Đường dẫn không hợp lệ", "Đường dẫn không được chứa dấu \" hoặc tab.")
            return
        projects = load_projects()
        name = slugify(os.path.basename(folder)) or "project"
        taken = {n for n, _ in projects} | {"root"}
        base, i = name, 2
        while name in taken:
            name, i = f"{base}-{i}", i + 1
        win = tk.Toplevel(self)
        win.title("Thêm dự án")
        win.transient(self)
        win.resizable(False, False)
        ttk.Label(win, text="Thư mục:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        ttk.Label(win, text=folder, foreground="#555").grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        ttk.Label(win, text="Tên dự án:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        var = tk.StringVar(value=name)
        ent = ttk.Entry(win, textvariable=var, width=30)
        ent.grid(row=1, column=1, sticky="w", padx=10)
        ttk.Label(win, text="Chỉ dùng a-z, 0-9, - và _ (thành địa chỉ <tên>.localhost và /<tên>/)",
                  foreground="#777").grid(row=2, column=0, columnspan=2, sticky="w", padx=10)

        def ok():
            n = var.get().strip().lower()
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", n) or n in taken:
                messagebox.showerror("Tên không hợp lệ", "Tên phải là a-z, 0-9, - hoặc _ và chưa dùng.", parent=win)
                return
            projects.append((n, folder))
            save_projects(projects)
            win.destroy()
            self.refresh_projects()
            self.log(f"Thêm dự án '{n}' -> {folder}")
            self.apply_projects()
        row = ttk.Frame(win)
        row.grid(row=3, column=0, columnspan=2, pady=10)
        cbtn(row, "Thêm", "green", ok, 8).pack(side="left", padx=4)
        cbtn(row, "Huỷ", "slate", win.destroy, 8).pack(side="left", padx=4)
        win.bind("<Return>", lambda e: ok())
        ent.focus_set()
        win.grab_set()

    def remove_project(self):
        sel = self._selected_project()
        if not sel:
            return
        if not messagebox.askyesno("Xoá dự án", f"Bỏ '{sel[0]}' khỏi danh sách?\n(Thư mục và file của bạn không bị xoá.)"):
            return
        save_projects([(n, f) for n, f in load_projects() if n != sel[0]])
        self.refresh_projects()
        self.log(f"Đã bỏ dự án '{sel[0]}'")
        self.apply_projects()

    def open_project(self, kind):
        sel = self._selected_project()
        if not sel:
            return
        svc = "Apache" if kind == "php" else "Tomcat"
        if not self.running(svc):
            messagebox.showinfo(f"Cần {svc}", f"Hãy Start {svc} trước (tab Dịch vụ).")
            return
        webbrowser.open(self._project_urls(sel[0])[0 if kind == "php" else 1])

    def open_project_folder(self):
        sel = self._selected_project()
        if sel:
            open_path(sel[1])

    def open_web(self, name):
        if name == "MySQL":
            if not self.running("Apache"):
                messagebox.showinfo("Cần Apache", "phpMyAdmin chạy qua Apache. Hãy Start Apache trước.")
                return
            url = f"http://localhost:{self.rows['Apache']['port']}/phpmyadmin/"
        else:
            url = f"http://localhost:{self.rows[name]['port']}/"
        webbrowser.open(url)


if __name__ == "__main__":
    Panel().mainloop()
