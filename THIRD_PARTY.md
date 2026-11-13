# Third-party software and trademarks

Lampcat's own code (the shell scripts, the control panel, the packaging files and the sample pages in
this repository) is released under the [MIT License](LICENSE).

Lampcat does **not** contain or modify any of the programs below. It configures and starts them:

| Program | How Lampcat gets it | License |
|---|---|---|
| Apache HTTP Server | installed from your distribution (`apache2`) | Apache-2.0 |
| PHP (+ `mod_php`) | installed from your distribution (`libapache2-mod-php`) | PHP License v3.01 |
| MariaDB Server | installed from your distribution (`mariadb-server`) | GPL-2.0 |
| Apache Tomcat 10.1 | downloaded from archive.apache.org by `setup.sh` | Apache-2.0 |
| phpMyAdmin 5.2 | downloaded from files.phpmyadmin.net by `setup.sh` | GPL-2.0-or-later |

The `.deb` package that `packaging/build-deb.sh` produces additionally **bundles the unmodified Tomcat and
phpMyAdmin release archives** so the first start works offline. They remain under their own licenses
above; their license files are inside those archives. Bundling them next to Lampcat's scripts is mere
aggregation and does not change the license of either side. If you redistribute that `.deb`, you take on
the obligations of those licenses (for phpMyAdmin: GPL, including offering the source, which is available
at https://www.phpmyadmin.net/).

## Trademarks

Lampcat is an independent project. It is **not affiliated with, endorsed by or sponsored by** Apache Friends,
the Apache Software Foundation, the phpMyAdmin project, the PHP Group or the MariaDB Foundation.

XAMPP is a trademark of Apache Friends. Apache, Apache HTTP Server, Apache Tomcat and the feather logo are
trademarks of the Apache Software Foundation. MariaDB is a trademark of the MariaDB Foundation.
phpMyAdmin is a trademark of the phpMyAdmin project. Product names are used here only to describe what
Lampcat controls.
