# Lampcat

**A one-window local web stack for Linux: Apache + PHP, MariaDB, Tomcat (JSP/Servlet) and phpMyAdmin.**
Put your code in one folder, press *Start All*, and PHP runs on Apache while JSP/servlets run on Tomcat,
from the same folder. It is the kind of thing XAMPP gives you on Windows, built for Linux and with Tomcat included.

[Tiếng Việt](README.vi.md) · [License: MIT](LICENSE) · [Third-party software & trademarks](THIRD_PARTY.md)

> **Status:** works, but young. It has only been tested on **Ubuntu 26.04**. Other Debian/Ubuntu-based
> releases should work but are untested. See [Limitations](#limitations).

---

## Contents
- [What you get](#what-you-get)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Using it](#using-it)
- [Several projects at once](#several-projects-at-once)
- [Ports, web root and config files](#ports-web-root-and-config-files)
- [Command line](#command-line)
- [Importing a database](#importing-a-database)
- [Security notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Uninstall](#uninstall)
- [Project layout](#project-layout)
- [License and trademarks](#license-and-trademarks)

## What you get

| Piece | Default port | Notes |
|---|---|---|
| Apache HTTP Server + PHP (`mod_php`) | **8000** | serves `*.php` from the web root |
| Apache Tomcat 10.1 | **8080** | serves `*.jsp` and servlets from the **same** web root |
| MariaDB | **3307** | user `root`, empty password, listens on `127.0.0.1` only |
| phpMyAdmin 5.2 | via Apache: `/phpmyadmin/` | logs in automatically, reachable only from this machine |

- A small Tk control panel: Start/Stop per service, *Start All / Stop All*, edit each port and save it, open the
  service in the browser, open its config file or log, and pick the web root with a folder chooser.
- **No sudo, no password prompts.** Everything runs as your user, on ports above 1024.
- It does **not** touch the system `apache2` / `mariadb` services, so it can run next to them.

## How it works

Lampcat does not bundle its own Apache, PHP or MariaDB. It uses the ones your distribution installed, but it runs
**its own instances** of them with configuration and data kept in one folder in your home directory:

- Apache is started with `apache2 -f <your folder>/apache/conf/httpd.conf`, with `DocumentRoot` set to the web root.
- MariaDB is started with its own `datadir`, socket and `my.cnf`.
- Tomcat is started from a private Tomcat directory whose root context points at the **same web root folder**.
- The panel only reads PID files, edits the port lines in the config files, and calls `lampcat.sh`.

Because Apache and Tomcat read the same folder, each one refuses what belongs to the other: Apache answers
`403` for `*.jsp`, `WEB-INF` and `META-INF`, and Tomcat answers `403` for `*.php`. Neither shows the other's source code.

## Requirements

- A Debian/Ubuntu-based Linux with a desktop session (the panel uses Tk).
- `apache2`, `libapache2-mod-php`, `php-mysql`, `mariadb-server`, a Java runtime, `python3-tk`, `curl`, `xdg-utils` (and `zenity` for a nicer folder picker, optional).
  The `.deb` package installs all of these for you. If you run from source you install them yourself:

```bash
sudo apt install apache2 libapache2-mod-php php-mysql php-mbstring php-xml php-curl php-gd php-zip \
                 mariadb-server default-jre python3-tk curl xdg-utils
```

You do **not** need to leave the system `apache2` and `mariadb` services running. If you don't use them for
anything else you can switch them off (`sudo systemctl disable --now apache2 mariadb`); Lampcat keeps working,
because it only needs their program files. **Do not uninstall those packages**, Lampcat depends on them.

## Install

### Option A: the `.deb` package (recommended)

Build it from this repository (needs `dpkg-deb`, `curl`; it downloads Tomcat and phpMyAdmin once into `dist/cache/`):

```bash
git clone https://github.com/tranvanhuy-hichan/lampcat-for-linux.git lampcat
cd lampcat
packaging/build-deb.sh                  # or: VERSION=1.3.1 packaging/build-deb.sh
sudo apt install ./dist/lampcat_*_all.deb
```

Then start **Lampcat** from the application menu, or run `lampcat` in a terminal. On first start it creates
`~/Lampcat/`, initialises the database and opens the panel; later starts are instant.

Upgrading: build or download the newer `.deb` and install it the same way. Your code, databases and settings in
`~/Lampcat/` are kept. The package replaces the earlier `xampp-linux` package (the old name of this project) and
keeps using `~/XamppLinux/` if you already had it.

### Option B: run from the source folder (no package)

```bash
git clone https://github.com/tranvanhuy-hichan/lampcat-for-linux.git lampcat
cd lampcat
./setup.sh                              # downloads Tomcat + phpMyAdmin, creates php.ini and the database
python3 panel/lampcat-panel.py
```

Here the checkout itself is the data folder (runtime files are git-ignored). Put your code in `www/`.

## Using it

1. Open Lampcat. Three rows: **Apache**, **MySQL** (MariaDB) and **Tomcat**, each *Stopped*.
2. Press **Start All** (or *Start* on a single row). A row turns green with *Running*.
3. Put code in the **web root** (`~/Lampcat/www/` by default; **Web root > Open folder** opens it).

| You put | It runs on | Address |
|---|---|---|
| `www/shop/index.php` | Apache | `http://localhost:8000/shop/` |
| `www/shop/index.jsp` | Tomcat | `http://localhost:8080/shop/` |
| a servlet class in `www/WEB-INF/classes` | Tomcat | per your `web.xml` / annotations |

New or edited files are picked up immediately; no restart is needed. A restart is only needed after you change
the web root or a port.

- **Open** on the MySQL row opens phpMyAdmin (Apache must be running).
- **Config** and **Logs** open the service's config file / log in your default editor.
- **Save port** rewrites the port in the right config file (a `.bak` is kept) and offers to restart the service.
- Folders without an index file show a directory listing on both servers.

## Several projects at once

Besides the single shared web root, the **Projects** tab (top right of the panel) serves any number of folders
side by side. Press **+ Add project**, pick a folder and give it a name:

| Runs on | Address |
|---|---|
| Apache (PHP) | `http://<name>.localhost:8000/` |
| Tomcat (JSP/servlets) | `http://localhost:8080/<name>/` |

Each project gets its own document root, so absolute links such as `/css/app.css` work. `*.localhost` resolves to
your machine by itself, so nothing needs to be added to `/etc/hosts`. Adding or removing a project reloads Apache and
Tomcat picks it up on its own; your folders are never modified or deleted. The list is kept in `projects.conf`.
All projects share one PHP configuration and one MariaDB, so give each project its own database name.

## Ports, web root and config files

| Setting | Where it lives | Changed from the panel |
|---|---|---|
| Apache port | `apache/conf/httpd.conf` (`Listen`, `ServerName`) | yes |
| MariaDB port | `mysql/my.cnf` (`port=`) | yes |
| Tomcat port | `tomcat/conf/server.xml` (HTTP connector) | yes |
| Web root | `config.env` (`WEB_ROOT=`) | yes (**Web root > Change...**) |
| PHP settings | `php/php.ini` | opens via the *php.ini* button |

`WEB_ROOT` is a path relative to the data folder, or an absolute path (any folder you like, for example a
folder of school or work projects). After changing it, restart Apache and Tomcat (the panel offers to).
phpMyAdmin lives outside the web root, so your folder only ever contains your own files.

The panel only accepts ports from 1024 to 65535. That is why Apache uses **8000** rather than 80.

## Command line

The panel is a thin layer over one script, so everything can be scripted:

```bash
~/Lampcat/lampcat.sh all start
~/Lampcat/lampcat.sh apache stop
~/Lampcat/lampcat.sh mysql restart
~/Lampcat/lampcat.sh all status

mariadb -h127.0.0.1 -P3307 -uroot        # database shell
```

Services are `apache`, `mysql`, `tomcat` or `all`; actions are `start`, `stop`, `restart`, `status`.
(From a source checkout the script is `./lampcat.sh`.)

## Importing a database

phpMyAdmin: open `http://localhost:8000/phpmyadmin/`, press **New**, create the database, open it, choose the
**Import** tab, pick your `.sql` file and press **Import**. A dump without a `CREATE DATABASE` line needs the
database to exist first. From the shell:

```bash
mariadb -h127.0.0.1 -P3307 -uroot -e "CREATE DATABASE mydb CHARACTER SET utf8mb4"
mariadb -h127.0.0.1 -P3307 -uroot mydb < dump.sql
```

### Connecting from PHP

`localhost` works as you would expect (`mysqli_connect("localhost", "root", "", "mydb")`). Lampcat points PHP's
default MySQL socket at its own MariaDB, so it does not hit the system server by accident. If you connect with
`127.0.0.1` over TCP, use **port 3307** (or whatever you set the port to).

## Security notes

This is a **development** tool. Please read this before putting anything sensitive in the web root.

- **Apache and Tomcat listen on all network interfaces.** Anyone on your Wi-Fi/LAN can open
  `http://<your-ip>:8000/` and `:8080`, and can download every file in the web root. Do **not** point the web root at
  a folder containing `.env` files, keys, database dumps or backups. Prefer pointing it at a single project.
- MariaDB listens on `127.0.0.1` only, and `root` has an **empty password**. That is fine for a machine only you use.
  Do not copy this setup to a server.
- phpMyAdmin logs in as `root` without asking and is restricted to local connections (`Require local`).
- Directory listing is on for convenience. Turn it off for Tomcat by setting `listings` to `false` in
  `tomcat/conf/web.xml`, and for Apache by removing `Indexes` from `Options` in `apache/conf/httpd.conf`.
- Ports above 1024 mean other local users on a shared machine can also bind them. Don't use this on shared hosts.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| *Port N is in use* when starting | Another program uses that port. Change it in the panel (**Save port**). Example: a Docker MySQL container mapped to `3307` clashes with Lampcat's MariaDB; set Lampcat's to `3308`. |
| PHP says `Access denied for user 'root'@'localhost'` | You are talking to the system MariaDB instead of Lampcat's. Lampcat's `php.ini` already fixes `localhost`; if you changed `mysqli.default_socket`, restore it, or connect to `127.0.0.1:3307`. |
| Tomcat shows *404 Not Found* at `/` | The web root has no `index.jsp`. Directory listing is enabled by default now; otherwise open the exact path, e.g. `/myproject/page.jsp`. |
| Apache won't start | See `apache/logs/error.log` (the **Logs** button). Common causes: port in use, or a PHP module version mismatch; re-run `setup.sh`, which re-detects the installed `libphp*.so`. |
| MariaDB won't start | See `mysql/logs/error.log`. If the data folder was created by a different MariaDB major version, move `mysql/data` away and re-run `setup.sh` (this creates an empty database; export first if you need the data). |
| First start fails | Read `~/Lampcat/setup.log`. |

## Limitations

- Tested only on Ubuntu 26.04 (PHP 8.5, MariaDB 11.8, Tomcat 10.1, Java 25). The Apache config loads the PHP module
  found by `setup.sh`; other PHP versions should work but have not been tried.
- phpMyAdmin 5.2.x officially supports PHP up to 8.3. It ran correctly on PHP 8.5 in testing, with deprecation
  notices hidden in `php.ini`; this may change with phpMyAdmin or PHP updates.
- Tomcat is 10.x (`jakarta.servlet.*`). Code written for `javax.servlet.*` needs Tomcat 9 or migration. The
  version is a variable in `setup.sh`/`packaging/build-deb.sh`, but only 10.1 has been tested.
- Servlets (compiled classes in `WEB-INF/classes`) have not been tested; JSP has.
- The control panel is X11/Wayland Tk. No autostart-at-login yet: you start the stack from the panel.
- MariaDB runs from a **private copy** of `/usr/sbin/mariadbd` (`mysql/base/`). Ubuntu's AppArmor profile only lets
  the system binary write to `/var/lib/mariadb`; a copy at another path is not confined by it. `setup.sh` refreshes
  the copy, so re-run it after a MariaDB package update.

## Uninstall

```bash
sudo apt remove lampcat            # removes the program; your data folder stays
rm -rf ~/Lampcat                   # deletes your databases and code in the default web root!
```

Stop the services first (panel *Stop All*, or `~/Lampcat/lampcat.sh all stop`).

## Project layout

```
lampcat.sh                 start/stop/status for apache | mysql | tomcat | all
setup.sh                   one-time, idempotent setup (php.ini, phpMyAdmin, Tomcat, database)
config.env                 WEB_ROOT=...
apache/conf/               httpd.conf and the phpMyAdmin snippet
mysql/my.cnf               MariaDB settings (port)
www/                       sample pages; the default web root when running from source
panel/lampcat-panel.py     the Tk control panel
packaging/                 launcher, .desktop file, icon, build-deb.sh
LICENSE  THIRD_PARTY.md
```

Created at run time (git-ignored): `tomcat/`, `phpmyadmin/`, `mysql/data/`, `mysql/base/`, `php/php.ini`, logs, `tmp/`.

## License and trademarks

MIT, see [LICENSE](LICENSE). Lampcat is not affiliated with Apache Friends (XAMPP), the Apache Software Foundation,
the phpMyAdmin project, the PHP Group or the MariaDB Foundation; names are used only to describe what it controls.
Details and the licenses of the bundled software: [THIRD_PARTY.md](THIRD_PARTY.md).
