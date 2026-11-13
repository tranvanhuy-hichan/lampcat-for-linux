<%@ page contentType="text/html;charset=UTF-8" %>
<!doctype html><html><body>
<h1>Hello from JSP (Tomcat)</h1>
<p>Server: <%= application.getServerInfo() %></p>
<p>Java: <%= System.getProperty("java.version") %></p>
<p>Time: <%= new java.util.Date() %></p>
<p>Same folder, PHP version: <a href="index.php">index.php</a> (Apache)</p>
</body></html>
