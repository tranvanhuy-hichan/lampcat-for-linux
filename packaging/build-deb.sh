#!/usr/bin/env bash
# Build dist/lampcat_<version>_all.deb from this folder.  Usage: packaging/build-deb.sh
set -eu
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VER="${VERSION:-1.4.0}"
PMA_VERSION="${PMA_VERSION:-5.2.3}"
TOMCAT_VERSION="${TOMCAT_VERSION:-10.1.61}"
CACHE="$SRC/dist/cache"; mkdir -p "$CACHE"

# bundled third-party files (cached between builds)
PMA="$CACHE/phpMyAdmin-$PMA_VERSION.tar.gz"
[ -f "$PMA" ] || curl -fL "https://files.phpmyadmin.net/phpMyAdmin/$PMA_VERSION/phpMyAdmin-$PMA_VERSION-all-languages.tar.gz" -o "$PMA"
TC="$CACHE/apache-tomcat-$TOMCAT_VERSION.tar.gz"
if [ ! -f "$TC" ]; then
  if [ -f "$HOME/Downloads/apache-tomcat-$TOMCAT_VERSION.tar.gz" ]; then cp "$HOME/Downloads/apache-tomcat-$TOMCAT_VERSION.tar.gz" "$TC"
  else curl -fL "https://archive.apache.org/dist/tomcat/tomcat-10/v$TOMCAT_VERSION/bin/apache-tomcat-$TOMCAT_VERSION.tar.gz" -o "$TC"; fi
fi

B="$(mktemp -d)/lampcat_${VER}_all"; APP="$B/opt/lampcat"
mkdir -p "$APP"/{panel,vendor} "$B"/DEBIAN "$B"/usr/bin "$B"/usr/share/applications "$B"/usr/share/icons/hicolor/scalable/apps
install -m755 "$SRC/lampcat.sh" "$SRC/setup.sh" "$APP/"
install -m755 "$SRC/panel/lampcat-panel.py" "$APP/panel/"
cp "$PMA" "$APP/vendor/phpMyAdmin.tar.gz"; cp "$TC" "$APP/vendor/tomcat.tar.gz"

# default config + sample site, copied to the user's folder on first run (never overwritten)
S="$APP/skel"; mkdir -p "$S/apache/conf/extra" "$S/mysql" "$S/www/hello"
cp "$SRC/apache/conf/httpd.conf" "$S/apache/conf/"; cp "$SRC/apache/conf/extra/phpmyadmin.conf" "$S/apache/conf/extra/"
cp "$SRC/mysql/my.cnf" "$S/mysql/"; cp "$SRC/config.env" "$S/"
cp "$SRC/www/index.php" "$SRC/www/index.jsp" "$S/www/"; cp "$SRC/www/hello/"* "$S/www/hello/"
cp "$SRC/README.md" "$SRC/README.vi.md" "$SRC/LICENSE" "$SRC/THIRD_PARTY.md" "$APP/"; printf '%s\n' "$VER" > "$APP/VERSION"
# a fresh httpd.conf must not carry a php module version from this machine
sed -i 's#modules/libphp[0-9.]*\.so#modules/libphp8.5.so#' "$S/apache/conf/httpd.conf"

install -m755 "$SRC/packaging/lampcat" "$B/usr/bin/lampcat"
install -m644 "$SRC/packaging/lampcat.desktop" "$B/usr/share/applications/lampcat.desktop"
install -m644 "$SRC/packaging/lampcat.svg" "$B/usr/share/icons/hicolor/scalable/apps/lampcat.svg"

cat > "$B/DEBIAN/control" <<CTL
Package: lampcat
Version: $VER
Section: web
Priority: optional
Architecture: all
Depends: python3, python3-tk, xdg-utils, curl, apache2, libapache2-mod-php, php-mysql, php-mbstring, php-xml, php-curl, php-gd, php-zip, mariadb-server, default-jre
Recommends: zenity
Installed-Size: $(du -sk "$B/opt" "$B/usr" | awk '{s+=$1} END {print s}')
Conflicts: xampp-linux
Replaces: xampp-linux
Maintainer: Lampcat <noreply@localhost>
Description: Local web stack (Apache+PHP, MariaDB, Tomcat, phpMyAdmin)
 One control panel to start/stop Apache, MariaDB and Tomcat and change their ports.
 Apache and Tomcat share one web root: put code there and PHP runs on Apache,
 JSP/servlets on Tomcat. Runs as your user, data lives in ~/Lampcat.
CTL
mkdir -p "$SRC/dist"
dpkg-deb --build --root-owner-group "$B" "$SRC/dist/lampcat_${VER}_all.deb" >/dev/null
ls -lh "$SRC/dist/lampcat_${VER}_all.deb"
