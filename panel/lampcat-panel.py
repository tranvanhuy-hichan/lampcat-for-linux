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
import webbrowser
from tkinter import filedialog, messagebox, ttk

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


def open_path(path):
    if os.path.exists(path):
        subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        messagebox.showinfo("Không tìm thấy", path + "\nchưa tồn tại.")


# -------------------------------------------------------------------- GUI
class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lampcat Control Panel")
        self.rows = {}

        ttk.Label(self, text="Lampcat Control Panel",
                  font=("TkDefaultFont", 14, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        ttk.Label(self, text=ROOT, foreground="#666").pack(anchor="w", padx=12)

        grid = ttk.Frame(self)
        grid.pack(fill="x", padx=12, pady=10)
        heads = ["Service", "Status", "Port", "", "Action", "", "", ""]
        for i, h in enumerate(heads):
            ttk.Label(grid, text=h, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=i, padx=5, sticky="w")
        for r, name in enumerate(SERVICES, start=1):
            self._build_row(grid, r, name)

        rootbar = ttk.Frame(self)
        rootbar.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(rootbar, text="Web root:", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.root_var = tk.StringVar(value=get_web_root())
        ttk.Entry(rootbar, textvariable=self.root_var, state="readonly").pack(
            side="left", fill="x", expand=True, padx=6)
        ttk.Button(rootbar, text="Change...", command=self.change_root).pack(side="left")
        ttk.Button(rootbar, text="Open folder",
                   command=lambda: open_path(get_web_root())).pack(side="left", padx=(6, 0))

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=12)
        ttk.Button(bar, text="Start All", command=lambda: self.all("start")).pack(side="left")
        ttk.Button(bar, text="Stop All", command=lambda: self.all("stop")).pack(side="left", padx=6)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="php.ini", command=lambda: open_path(p("php", "php.ini"))).pack(side="left", padx=6)
        ttk.Button(bar, text="Clear log", command=lambda: self.log_w.delete("1.0", "end")).pack(side="right")

        self.log_w = tk.Text(self, height=10, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#fff")
        self.log_w.pack(fill="both", expand=True, padx=12, pady=10)
        self.log("Sẵn sàng. Đặt code (PHP, JSP, servlet) vào Web root: Apache chạy PHP, Tomcat chạy JSP/servlet.")
        self.poll()
        self.fit_to_content()

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
        row["status"] = ttk.Label(grid, text="...", width=9)
        row["status"].grid(row=r, column=1, padx=5, sticky="w")
        row["var"] = tk.StringVar(value=str(row["port"] or ""))
        ttk.Entry(grid, textvariable=row["var"], width=7).grid(row=r, column=2, padx=5)
        ttk.Button(grid, text="Save port", command=lambda n=name: self.save_port(n)).grid(row=r, column=3, padx=5)
        row["btn"] = ttk.Button(grid, text="Start", width=7, command=lambda n=name: self.toggle(n))
        row["btn"].grid(row=r, column=4, padx=5)
        ttk.Button(grid, text="Open", width=6, command=lambda n=name: self.open_web(n)).grid(row=r, column=5, padx=3)
        ttk.Button(grid, text="Config", width=7, command=lambda c=s["conf"]: open_path(c)).grid(row=r, column=6, padx=3)
        ttk.Button(grid, text="Logs", width=6, command=lambda l=s["log"]: open_path(l)).grid(row=r, column=7, padx=3)
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
            row["status"].config(text="Running" if up else "Stopped",
                                 foreground="#1a7f37" if up else "#666666")
            if not row["busy"]:
                row["btn"].config(text="Stop" if up else "Start")
        self.after(1500, self.poll)

    # ---- actions
    def run_async(self, name, fn):
        row = self.rows[name]
        if row["busy"]:
            return
        row["busy"] = True
        row["btn"].state(["disabled"])

        def work():
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                self.tlog(f"[{name}] LỖI: {e}")
            finally:
                def done():
                    row["busy"] = False
                    row["btn"].state(["!disabled"])
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
            self.tlog(f"[{name}] port {old} -> {new} (sửa {n} dòng, có file .bak)")
            if restart:
                self._exec(name, "restart")
            elif was_up:
                self.tlog(f"[{name}] cần Stop/Start để dùng port mới")
        self.run_async(name, work)

    def change_root(self):
        new = filedialog.askdirectory(title="Chọn thư mục gốc (web root)",
                                      initialdir=get_web_root(), mustexist=True)
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
