<?php
if (isset($_GET["info"])) { phpinfo(); exit; }
$root = dirname(__DIR__);
$ini  = @parse_ini_file($root . '/mysql/my.cnf', true, INI_SCANNER_RAW);
$myPort = $ini['mysqld']['port'] ?? 3306;
$tcXml = @file_get_contents($root . '/tomcat/conf/server.xml');
preg_match('/<Connector\s+port="(\d+)"\s+protocol="HTTP\/1\.1"/s', (string) $tcXml, $m);
$tcPort = $m[1] ?? 8080;
$host = preg_replace('/:\d+$/', '', $_SERVER['HTTP_HOST']);
$sites = array_filter(scandir(__DIR__), fn($d) => $d[0] !== '.' && is_dir(__DIR__ . "/$d") && $d !== 'phpmyadmin');
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lampcat</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;margin:0;background:#f6f6f4;color:#222}
main{max-width:760px;margin:0 auto;padding:32px 16px}
h1{margin:0 0 4px} p.sub{color:#666;margin:0 0 24px}
.card{background:#fff;border:1px solid #ddd;border-radius:10px;padding:16px 20px;margin-bottom:16px}
.card h2{margin:0 0 8px;font-size:1rem;color:#fb7a24}
a{color:#0b62c4} code{background:#eee;padding:1px 5px;border-radius:4px}
ul{margin:0;padding-left:20px}
</style></head><body><main>
<h1>Lampcat</h1>
<p class="sub">Apache + PHP <?= PHP_VERSION ?> &middot; MariaDB &middot; Tomcat &middot; phpMyAdmin</p>
<div class="card"><h2>Tools</h2><ul>
<li><a href="/phpmyadmin/">phpMyAdmin</a> (MariaDB on port <?= (int) $myPort ?>)</li>
<li><a href="http://<?= htmlspecialchars($host) ?>:<?= (int) $tcPort ?>/">Tomcat</a> (port <?= (int) $tcPort ?>) &middot;
    <a href="http://<?= htmlspecialchars($host) ?>:<?= (int) $tcPort ?>/hello/">JSP sample</a></li>
<li><a href="?info=1">phpinfo()</a></li></ul></div>
<div class="card"><h2>Your sites in the web root <code>www/</code></h2>
<?php if ($sites): ?><ul><?php foreach ($sites as $s): ?><li><a href="/<?= rawurlencode($s) ?>/"><?= htmlspecialchars($s) ?></a></li><?php endforeach ?></ul>
<?php else: ?>Empty. Put a folder here and open it in the browser.<?php endif ?></div>
</main></body></html>
