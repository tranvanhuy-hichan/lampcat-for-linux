# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue. Use GitHub's private reporting:
<https://github.com/tranvanhuy-hichan/lampcat-for-linux/security/advisories/new>

Include steps to reproduce, the affected version and the impact. We aim to acknowledge within 7 days.

## Scope notes

Lampcat is a **development** tool: Apache and Tomcat listen on all interfaces and MariaDB root has an empty password by default (see the README's Security notes). Reports about these documented defaults are not vulnerabilities, but anything that goes beyond them (for example remote code execution, path traversal, or privilege escalation from the control panel) is.
