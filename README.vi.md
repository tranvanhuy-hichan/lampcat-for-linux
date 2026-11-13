# Lampcat

**Bộ web cục bộ trên Linux, gói trong một cửa sổ: Apache + PHP, MariaDB, Tomcat (JSP/Servlet) và phpMyAdmin.**
Bạn đặt code vào một thư mục, bấm *Start All*, và PHP chạy trên Apache còn JSP/servlet chạy trên Tomcat, cùng từ một
thư mục. Nó làm việc giống XAMPP trên Windows, nhưng dành cho Linux và có sẵn Tomcat.

[English](README.md) · [Giấy phép MIT](LICENSE) · [Phần mềm bên thứ ba và nhãn hiệu](THIRD_PARTY.md)

> **Tình trạng:** chạy được nhưng còn mới. Mới thử trên **Ubuntu 26.04**. Các bản Debian/Ubuntu khác nhiều khả năng chạy
> được nhưng chưa thử. Xem mục [Hạn chế](#hạn-chế).

## Mục lục
[Có gì trong đó](#có-gì-trong-đó) · [Cách hoạt động](#cách-hoạt-động) · [Yêu cầu](#yêu-cầu) · [Cài đặt](#cài-đặt) ·
[Cách dùng](#cách-dùng) · [Cổng, thư mục gốc, cấu hình](#cổng-thư-mục-gốc-cấu-hình) · [Dòng lệnh](#dòng-lệnh) ·
[Nhập database](#nhập-database) · [Lưu ý bảo mật](#lưu-ý-bảo-mật) · [Gỡ lỗi](#gỡ-lỗi) · [Hạn chế](#hạn-chế) · [Gỡ cài đặt](#gỡ-cài-đặt)

## Có gì trong đó

| Thành phần | Cổng mặc định | Ghi chú |
|---|---|---|
| Apache HTTP Server + PHP (`mod_php`) | **8000** | chạy file `*.php` trong thư mục gốc |
| Apache Tomcat 10.1 | **8080** | chạy `*.jsp` và servlet từ **cùng** thư mục gốc |
| MariaDB | **3307** | tài khoản `root`, mật khẩu rỗng, chỉ nhận kết nối từ `127.0.0.1` |
| phpMyAdmin 5.2 | qua Apache: `/phpmyadmin/` | đăng nhập sẵn, chỉ truy cập được từ chính máy này |

- Một bảng điều khiển Tk nhỏ: Start/Stop từng dịch vụ, *Start All / Stop All*, sửa và lưu cổng, mở dịch vụ trên trình duyệt,
  mở file cấu hình hoặc log, và chọn thư mục gốc bằng hộp thoại chọn thư mục.
- **Không cần sudo, không hỏi mật khẩu.** Mọi thứ chạy bằng quyền user của bạn, ở cổng trên 1024.
- **Không đụng** vào dịch vụ `apache2` và `mariadb` của hệ thống, nên chạy song song được với chúng.

## Cách hoạt động

Lampcat không tự đóng gói Apache, PHP hay MariaDB. Nó dùng bản mà hệ điều hành đã cài, nhưng chạy **bản riêng (tiến trình riêng)**
của chúng, với cấu hình và dữ liệu nằm trong một thư mục ở thư mục home của bạn:

- Apache chạy bằng `apache2 -f <thư mục của bạn>/apache/conf/httpd.conf`, với `DocumentRoot` là thư mục gốc.
- MariaDB chạy với `datadir`, socket và `my.cnf` riêng.
- Tomcat chạy từ một thư mục Tomcat riêng, có ngữ cảnh gốc trỏ vào **chính thư mục gốc đó**.
- Bảng điều khiển chỉ đọc file PID, sửa dòng cổng trong file cấu hình và gọi `lampcat.sh`.

Vì Apache và Tomcat đọc cùng một thư mục, mỗi bên từ chối thứ thuộc về bên kia: Apache trả `403` cho `*.jsp`, `WEB-INF`,
`META-INF`, còn Tomcat trả `403` cho `*.php`. Không bên nào để lộ mã nguồn của bên kia.

## Yêu cầu

- Linux nền Debian/Ubuntu, có giao diện đồ họa (bảng điều khiển dùng Tk).
- `apache2`, `libapache2-mod-php`, `php-mysql`, `mariadb-server`, Java, `python3-tk`, `curl`, `xdg-utils`.
  Gói `.deb` tự cài các thứ này. Nếu chạy từ mã nguồn thì bạn tự cài:

```bash
sudo apt install apache2 libapache2-mod-php php-mysql php-mbstring php-xml php-curl php-gd php-zip \
                 mariadb-server default-jre python3-tk curl xdg-utils
```

Bạn **không cần** để dịch vụ `apache2` và `mariadb` của hệ thống chạy. Nếu không dùng cho việc khác, bạn tắt được
(`sudo systemctl disable --now apache2 mariadb`), Lampcat vẫn chạy vì nó chỉ cần file chương trình của chúng.
**Đừng gỡ các gói đó**, Lampcat phụ thuộc vào chúng.

## Cài đặt

### Cách A: gói `.deb` (khuyên dùng)

Build từ repo này (cần `dpkg-deb`, `curl`; tải Tomcat và phpMyAdmin một lần vào `dist/cache/`):

```bash
git clone https://github.com/tranvanhuy-hichan/lampcat-for-linux.git lampcat
cd lampcat
packaging/build-deb.sh                  # hoặc: VERSION=1.2.0 packaging/build-deb.sh
sudo apt install ./dist/lampcat_*_all.deb
```

Sau đó mở **Lampcat** trong menu ứng dụng, hoặc gõ `lampcat` trong terminal. Lần đầu nó tạo thư mục `~/Lampcat/`,
khởi tạo database rồi mở bảng điều khiển; các lần sau mở ngay.

Nâng cấp: build hoặc tải `.deb` mới và cài lại giống trên. Code, database và cài đặt trong `~/Lampcat/` được giữ nguyên.
Gói thay thế gói `xampp-linux` cũ (tên cũ của dự án) và vẫn dùng `~/XamppLinux/` nếu bạn đã có thư mục này.

### Cách B: chạy thẳng từ thư mục mã nguồn (không cần cài gói)

```bash
git clone https://github.com/tranvanhuy-hichan/lampcat-for-linux.git lampcat
cd lampcat
./setup.sh                              # tải Tomcat + phpMyAdmin, tạo php.ini và database
python3 panel/lampcat-panel.py
```

Ở cách này, thư mục clone chính là thư mục dữ liệu (file sinh ra khi chạy đã được git bỏ qua). Đặt code vào `www/`.

## Cách dùng

1. Mở Lampcat. Có ba dòng: **Apache**, **MySQL** (MariaDB) và **Tomcat**, đều đang *Stopped*.
2. Bấm **Start All** (hoặc *Start* ở từng dòng). Dòng chạy sẽ chuyển sang chữ *Running* màu xanh.
3. Đặt code vào **thư mục gốc** (mặc định `~/Lampcat/www/`; bấm **Web root > Open folder** để mở).

| Bạn đặt | Chạy trên | Địa chỉ |
|---|---|---|
| `www/shop/index.php` | Apache | `http://localhost:8000/shop/` |
| `www/shop/index.jsp` | Tomcat | `http://localhost:8080/shop/` |
| class servlet trong `www/WEB-INF/classes` | Tomcat | theo `web.xml` hoặc annotation |

File mới hoặc vừa sửa được nhận ngay, không cần khởi động lại. Chỉ cần khởi động lại sau khi đổi thư mục gốc hoặc đổi cổng.

- **Open** ở dòng MySQL mở phpMyAdmin (Apache phải đang chạy).
- **Config** và **Logs** mở file cấu hình hoặc log của dịch vụ bằng trình soạn thảo mặc định.
- **Save port** ghi lại cổng vào đúng file cấu hình (giữ file `.bak`) và hỏi có khởi động lại dịch vụ không.
- Thư mục không có file index sẽ hiện danh sách file trên cả hai server.

## Cổng, thư mục gốc, cấu hình

| Thiết lập | Nằm ở đâu | Đổi được trên panel |
|---|---|---|
| Cổng Apache | `apache/conf/httpd.conf` (`Listen`, `ServerName`) | có |
| Cổng MariaDB | `mysql/my.cnf` (`port=`) | có |
| Cổng Tomcat | `tomcat/conf/server.xml` (connector HTTP) | có |
| Thư mục gốc | `config.env` (`WEB_ROOT=`) | có (**Web root > Change...**) |
| Cài đặt PHP | `php/php.ini` | mở bằng nút *php.ini* |

`WEB_ROOT` là đường dẫn tương đối so với thư mục dữ liệu, hoặc đường dẫn tuyệt đối (thư mục nào cũng được, ví dụ thư mục
chứa các bài tập hay project). Sau khi đổi, khởi động lại Apache và Tomcat (panel sẽ hỏi). phpMyAdmin nằm ngoài thư mục gốc,
nên thư mục của bạn chỉ chứa file của bạn.

Panel chỉ nhận cổng từ 1024 đến 65535. Vì vậy Apache dùng cổng **8000** chứ không phải 80.

## Dòng lệnh

Panel chỉ là lớp mỏng bên trên một script, nên dùng script được hết:

```bash
~/Lampcat/lampcat.sh all start
~/Lampcat/lampcat.sh apache stop
~/Lampcat/lampcat.sh mysql restart
~/Lampcat/lampcat.sh all status

mariadb -h127.0.0.1 -P3307 -uroot        # vào dòng lệnh database
```

Dịch vụ là `apache`, `mysql`, `tomcat` hoặc `all`; hành động là `start`, `stop`, `restart`, `status`.
(Nếu chạy từ mã nguồn thì script là `./lampcat.sh`.)

## Nhập database

phpMyAdmin: mở `http://localhost:8000/phpmyadmin/`, bấm **New** để tạo database, mở nó ra, chọn tab **Import**, chọn file `.sql`
rồi bấm **Import**. File dump không có dòng `CREATE DATABASE` thì phải tạo database trước. Dùng dòng lệnh:

```bash
mariadb -h127.0.0.1 -P3307 -uroot -e "CREATE DATABASE mydb CHARACTER SET utf8mb4"
mariadb -h127.0.0.1 -P3307 -uroot mydb < dump.sql
```

### Kết nối từ PHP

`localhost` dùng bình thường (`mysqli_connect("localhost", "root", "", "mydb")`). Lampcat trỏ socket MySQL mặc định của PHP
vào MariaDB của nó, nên không nối nhầm sang server của hệ thống. Nếu bạn kết nối bằng `127.0.0.1` qua TCP thì dùng **cổng 3307**
(hoặc cổng bạn đã đặt).

## Lưu ý bảo mật

Đây là công cụ **để phát triển**. Hãy đọc kỹ trước khi đặt thứ nhạy cảm vào thư mục gốc.

- **Apache và Tomcat lắng nghe trên mọi giao diện mạng.** Ai cùng Wi-Fi hoặc mạng LAN với bạn mở được
  `http://<ip-của-bạn>:8000/` và `:8080`, và tải được mọi file trong thư mục gốc. **Đừng** đặt thư mục gốc vào chỗ có file `.env`,
  khóa, file dump database hay bản sao lưu. Nên trỏ vào đúng một project.
- MariaDB chỉ lắng nghe trên `127.0.0.1`, và `root` có **mật khẩu rỗng**. Vậy là ổn cho máy chỉ mình bạn dùng.
  Đừng mang cấu hình này lên máy chủ thật.
- phpMyAdmin tự đăng nhập bằng `root` và chỉ cho kết nối từ chính máy này (`Require local`).
- Liệt kê thư mục được bật cho tiện. Tắt ở Tomcat bằng cách đặt `listings` thành `false` trong `tomcat/conf/web.xml`, tắt ở Apache
  bằng cách bỏ `Indexes` khỏi `Options` trong `apache/conf/httpd.conf`.
- Không dùng trên máy dùng chung với nhiều người.

## Gỡ lỗi

| Vấn đề | Nguyên nhân và cách xử lý |
|---|---|
| Báo *Port N đang bị chiếm* khi Start | Có chương trình khác dùng cổng đó. Đổi cổng trên panel (**Save port**). Ví dụ: container MySQL của Docker map ra `3307` sẽ đụng MariaDB của Lampcat; đặt Lampcat sang `3308`. |
| PHP báo `Access denied for user 'root'@'localhost'` | Bạn đang nối vào MariaDB của hệ thống chứ không phải của Lampcat. `php.ini` của Lampcat đã sửa cho `localhost`; nếu bạn đã đổi `mysqli.default_socket` thì khôi phục lại, hoặc kết nối tới `127.0.0.1:3307`. |
| Tomcat báo *404 Not Found* ở `/` | Thư mục gốc không có `index.jsp`. Mặc định đã bật liệt kê thư mục; nếu không, mở đúng đường dẫn, ví dụ `/myproject/page.jsp`. |
| Apache không chạy | Xem `apache/logs/error.log` (nút **Logs**). Thường do cổng bị chiếm hoặc lệch phiên bản module PHP; chạy lại `setup.sh` để nó dò lại `libphp*.so` đã cài. |
| MariaDB không chạy | Xem `mysql/logs/error.log`. Nếu thư mục dữ liệu tạo bởi MariaDB bản chính khác, dời `mysql/data` đi và chạy lại `setup.sh` (sẽ tạo database rỗng; xuất dữ liệu ra trước nếu cần). |
| Lần chạy đầu bị lỗi | Đọc `~/Lampcat/setup.log`. |

## Hạn chế

- Mới thử trên Ubuntu 26.04 (PHP 8.5, MariaDB 11.8, Tomcat 10.1, Java 25). Cấu hình Apache nạp module PHP mà `setup.sh` tìm thấy;
  các bản PHP khác nhiều khả năng chạy được nhưng chưa thử.
- phpMyAdmin 5.2.x chính thức hỗ trợ PHP đến 8.3. Khi thử nó vẫn chạy đúng trên PHP 8.5, với cảnh báo deprecated bị ẩn trong `php.ini`;
  điều này có thể thay đổi theo bản cập nhật của phpMyAdmin hoặc PHP.
- Tomcat là bản 10.x (`jakarta.servlet.*`). Code viết cho `javax.servlet.*` cần Tomcat 9 hoặc phải chuyển đổi. Số phiên bản là biến trong
  `setup.sh` và `packaging/build-deb.sh`, nhưng mới chỉ thử bản 10.1.
- Servlet (class đã biên dịch trong `WEB-INF/classes`) chưa được thử; JSP thì đã thử.
- Chưa có tự khởi động khi đăng nhập: bạn bật dịch vụ từ panel.
- MariaDB chạy từ **một bản sao riêng** của `/usr/sbin/mariadbd` (`mysql/base/`). Profile AppArmor của Ubuntu chỉ cho bản hệ thống ghi vào
  `/var/lib/mariadb`; bản sao ở đường dẫn khác không bị profile đó giới hạn. `setup.sh` làm mới bản sao, nên chạy lại sau khi cập nhật gói MariaDB.

## Gỡ cài đặt

```bash
sudo apt remove lampcat            # gỡ chương trình; thư mục dữ liệu của bạn vẫn còn
rm -rf ~/Lampcat                   # xóa database và code trong thư mục gốc mặc định!
```

Hãy dừng dịch vụ trước (panel *Stop All* hoặc `~/Lampcat/lampcat.sh all stop`).

## Giấy phép và nhãn hiệu

MIT, xem [LICENSE](LICENSE). Lampcat không liên kết với Apache Friends (XAMPP), Apache Software Foundation, dự án phpMyAdmin,
PHP Group hay MariaDB Foundation; tên của họ chỉ được dùng để mô tả thứ mà nó điều khiển.
Chi tiết và giấy phép của phần mềm đi kèm: [THIRD_PARTY.md](THIRD_PARTY.md).
