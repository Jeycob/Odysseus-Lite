# Changelog

## 0.3.2

- Validate `/data/odysseus/auth.json` on every start.
- Create an initial admin account when `auth.json` is missing, invalid, or has
  no users.
- Preserve and normalize legacy single-user auth files.
- Add `reset_admin_password_on_start` for explicit admin password recovery.
- Document first login, reset flow, and local-vs-GitHub add-on data separation.

## 0.3.1

- Fix Odysseus API calls inside Home Assistant Ingress by rewriting same-origin
  absolute URLs such as `http://homeassistant.local/api/sessions` to the
  Ingress base path.
- Stop rewriting normal JSON API responses in the proxy.

## 0.3.0

- Route Home Assistant Ingress through a local wrapper on port 8099.
- Strip iframe-blocking security headers only for Ingress traffic.
- Rewrite absolute Odysseus asset/API paths to the Home Assistant Ingress base
  path.

## 0.2.0

- Add Home Assistant Ingress support.
- Add Odysseus to the Home Assistant sidebar.
- Keep the direct web UI available on port 7000.

## 0.1.0

- Initial experimental single-container Odysseus add-on.
