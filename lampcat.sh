#!/usr/bin/env bash
# Control the local stack.   Usage: ./lampcat.sh <apache|mysql|tomcat|all> <start|stop|restart|status>
# Everything runs as the current user (no sudo), using config/data inside this folder.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export XROOT="$ROOT"                     # used by php.ini and httpd.conf

APACHE_BIN="${APACHE_BIN:-/usr/sbin/apache2}"
MARIADB_BIN="${MARIADB_BIN:-$ROOT/mysql/base/sbin/mariadbd}"

# Shared web root: WEB_ROOT in config.env (relative paths are relative to this folder)
WEB_ROOT="$(sed -n 's/^WEB_ROOT=//p' "$ROOT/config.env" 2>/dev/null | tail -n1 | sed -e 's/^"//' -e 's/"$//')"
WEB_ROOT="${WEB_ROOT:-www}"
case "$WEB_ROOT" in /*) ;; *) WEB_ROOT="$ROOT/$WEB_ROOT" ;; esac
WEB_ROOT="${WEB_ROOT%/}"
check_root() { [ -d "$WEB_ROOT" ] || { echo "Web root not found: $WEB_ROOT (fix WEB_ROOT in config.env)"; return 1; }; }

APACHE_PID="$ROOT/apache/run/httpd.pid"
MYSQL_PID="$ROOT/mysql/run/mysqld.pid"
TOMCAT_PID="$ROOT/tomcat/temp/catalina.pid"

alive() { [ -f "$1" ] && kill -0 "$(cat "$1" 2>/dev/null)" 2>/dev/null; }

wait_for() {  # wait_for <seconds> <command...>
  local n=$(( $1 * 2 )); shift
  while [ $n -gt 0 ]; do "$@" && return 0; sleep 0.5; n=$((n-1)); done
  return 1
}
gone() { ! alive "$1"; }

# ---------------------------------------------------------------- apache
apache_cmd() {
  "$APACHE_BIN" -d "$ROOT/apache" -f "$ROOT/apache/conf/httpd.conf" \
    -C "Define XROOT \"$ROOT\"" -C "Define WEBROOT \"$WEB_ROOT\"" -k "$1"
}
apache_start() {
  alive "$APACHE_PID" && { echo "Apache already running"; return 0; }
  check_root || return 1
  mkdir -p "$ROOT/apache/run" "$ROOT/apache/logs" "$ROOT/tmp/sessions" "$ROOT/tmp/uploads"
  apache_cmd start || return 1
  wait_for 10 alive "$APACHE_PID" && echo "Apache started" || { echo "Apache failed - see apache/logs/error.log"; return 1; }
}
apache_stop() {
  alive "$APACHE_PID" || { echo "Apache not running"; return 0; }
  apache_cmd stop
  wait_for 15 gone "$APACHE_PID" && echo "Apache stopped" || { echo "Apache did not stop"; return 1; }
}

# ----------------------------------------------------------------- mysql
mysql_start() {
  alive "$MYSQL_PID" && { echo "MariaDB already running"; return 0; }
  [ -d "$ROOT/mysql/data/mysql" ] || { echo "MariaDB data dir not initialised - run ./setup.sh"; return 1; }
  mkdir -p "$ROOT/mysql/run" "$ROOT/mysql/logs" "$ROOT/mysql/tmp"
  rm -f "$MYSQL_PID"
  setsid nohup "$MARIADB_BIN" --defaults-file="$ROOT/mysql/my.cnf" --basedir="$ROOT/mysql/base" \
    --datadir="$ROOT/mysql/data" --socket="$ROOT/mysql/run/mysqld.sock" \
    --pid-file="$MYSQL_PID" --log-error="$ROOT/mysql/logs/error.log" \
    --tmpdir="$ROOT/mysql/tmp" >/dev/null 2>&1 &
  wait_for 30 alive "$MYSQL_PID" && echo "MariaDB started" || { echo "MariaDB failed - see mysql/logs/error.log"; tail -n 5 "$ROOT/mysql/logs/error.log" 2>/dev/null; return 1; }
}
mysql_stop() {
  alive "$MYSQL_PID" || { echo "MariaDB not running"; return 0; }
  kill -TERM "$(cat "$MYSQL_PID")"
  wait_for 40 gone "$MYSQL_PID" && echo "MariaDB stopped" || { echo "MariaDB did not stop"; return 1; }
}

# ---------------------------------------------------------------- tomcat
tomcat_env() {
  export CATALINA_HOME="$ROOT/tomcat" CATALINA_BASE="$ROOT/tomcat" CATALINA_PID="$TOMCAT_PID"
  if [ -z "${JAVA_HOME:-}" ] && command -v java >/dev/null; then
    JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"; export JAVA_HOME
  fi
}
# Make Tomcat's root context point at the shared web root.
tomcat_sync_root() {
  local d="$ROOT/tomcat/conf/Catalina/localhost"
  mkdir -p "$d"
  printf '<Context docBase="%s" reloadable="false" />\n' "$WEB_ROOT" > "$d/ROOT.xml"
  if [ -d "$ROOT/tomcat/webapps/ROOT" ]; then   # stock ROOT app would clash with ours
    mkdir -p "$ROOT/tomcat/ROOT.default"; mv "$ROOT/tomcat/webapps/ROOT/"* "$ROOT/tomcat/ROOT.default/" 2>/dev/null
    rmdir "$ROOT/tomcat/webapps/ROOT" 2>/dev/null
  fi
}
tomcat_start() {
  alive "$TOMCAT_PID" && { echo "Tomcat already running"; return 0; }
  check_root || return 1
  tomcat_sync_root
  tomcat_env
  "$CATALINA_HOME/bin/startup.sh" >/dev/null 2>&1
  wait_for 20 alive "$TOMCAT_PID" && echo "Tomcat started" || { echo "Tomcat failed - see tomcat/logs/catalina.out"; return 1; }
}
tomcat_stop() {
  alive "$TOMCAT_PID" || { echo "Tomcat not running"; return 0; }
  tomcat_env
  "$CATALINA_HOME/bin/shutdown.sh" >/dev/null 2>&1
  wait_for 30 gone "$TOMCAT_PID" && echo "Tomcat stopped" || { echo "Tomcat did not stop"; return 1; }
}

# ---------------------------------------------------------------- status
status_of() {
  local pidf; case "$1" in apache) pidf=$APACHE_PID;; mysql) pidf=$MYSQL_PID;; tomcat) pidf=$TOMCAT_PID;; esac
  if alive "$pidf"; then echo "$1: running"; return 0; else echo "$1: stopped"; return 1; fi
}

svc="${1:-}"; act="${2:-}"
run() {  # run <service> <action>
  case "$2" in
    start|stop) "${1}_$2" ;;
    restart) "${1}_stop"; "${1}_start" ;;
    status) status_of "$1" ;;
    *) return 2 ;;
  esac
}
case "$svc" in
  apache|mysql|tomcat) run "$svc" "$act"; exit $? ;;
  all)
    rc=0
    if [ "$act" = stop ]; then order="tomcat apache mysql"; else order="mysql apache tomcat"; fi
    for s in $order; do run "$s" "$act" || rc=1; done
    exit $rc ;;
  *) echo "Usage: $0 <apache|mysql|tomcat|all> <start|stop|restart|status>"; exit 2 ;;
esac
