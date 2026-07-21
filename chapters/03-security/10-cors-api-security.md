# CORS & API Security

Cross-Origin Resource Sharing (CORS) is a browser policy controlled by HTTP response headers. It decides whether JavaScript from one origin may read a response from another; it does not replace authentication, authorization or server-side input validation.

## When CORS Is Needed

Use CORS only when a separately hosted browser application must call a WordPress API. A normal WordPress theme, server-to-server integration or webhook does not need it.

```text
Browser app at https://app.example
  → browser requests https://api.example/wp-json/...
  → API explicitly allows the known origin and required method
```

Keep the allowlist specific. Do not reflect an arbitrary `Origin` header and do not use `*` for an authenticated response.

## Credentials and Preflight

If a browser request uses cookies or another credential mode, the server must explicitly allow the exact origin and credentials. Wildcard origins cannot be used for credentialed cross-origin responses. Non-simple requests can trigger a preflight `OPTIONS` request; allow only the methods and request headers the API actually needs.

Regardless of CORS, every custom WordPress REST route needs a `permission_callback`, input validation and rate-limit/abuse considerations. CORS only protects browser access to the response; it does not stop a script, server or attacker from sending an HTTP request directly.

## Validation Checklist

- [ ] The API has a documented set of trusted frontend origins.
- [ ] Anonymous and authenticated endpoints have separate access expectations.
- [ ] Preflight responses allow only required methods and headers.
- [ ] Credentialed routes never send wildcard access-control origins.
- [ ] Browser, server-to-server and webhook tests all use their correct authentication model.

Further reading: [MDN CORS guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS), [WordPress REST API](../08-plugin-development/06-rest-api.md) and [Integration Architecture](../10-platform-architecture-governance/07-integration-architecture.md).
