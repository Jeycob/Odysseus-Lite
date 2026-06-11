# Changelog

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
