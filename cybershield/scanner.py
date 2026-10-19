"""Small, non-intrusive HTTP security configuration auditor.

Safety characteristics:
- GET requests to the supplied page only; no directory discovery or exploitation.
- At most one normal request chain plus one optional Origin probe.
- Denies localhost, private/reserved IPs and internal redirect destinations.
- TLS certificate verification is enabled by the Python standard library.
- Does not save cookie values or application response bodies.

Caveat: DNS checks are best effort, not a protection against DNS rebinding.
Keep the Streamlit frontend local; do not expose it as a public URL scanner.
"""

from __future__ import annotations

import http.client
import ipaddress
import re
import socket
import ssl
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urljoin, urlsplit

USER_AGENT = "CyberShield-PassiveAuditor/1.0 (authorized configuration review)"
PROBE_ORIGIN = "https://cybershield-audit.invalid"
MAX_REDIRECTS = 3


class ScanError(Exception):
    """An audit could not be safely or reliably completed."""


@dataclass(frozen=True)
class ResponseSnapshot:
    url: str
    status: int
    headers: tuple[tuple[str, str], ...]

    def get(self, key: str, default: str = "") -> str:
        return next((v for k, v in self.headers if k.lower() == key.lower()), default)

    def get_all(self, key: str) -> list[str]:
        return [v for k, v in self.headers if k.lower() == key.lower()]


@dataclass(frozen=True)
class Finding:
    key: str
    title: str
    status: str
    severity: str
    detail: str
    recommendation: str
    evidence: str = ""


@dataclass(frozen=True)
class AuditResult:
    target_url: str
    final_url: str
    scanned_at: str
    http_status: int
    score: int
    grade: str
    findings: tuple[Finding, ...]
    redirects: tuple[str, ...]
    elapsed_ms: int
    demo: bool = False

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["summary"] = {
            "warnings": sum(f.status == "WARN" for f in self.findings),
            "passed": sum(f.status == "PASS" for f in self.findings),
            "informational": sum(f.status == "INFO" for f in self.findings),
            "total_checks": len(self.findings),
        }
        payload["disclaimer"] = (
            "Indicative, page-level configuration audit only. "
            "Not a vulnerability scan, penetration test, or security certification."
        )
        return payload


def normalize_url(value: str) -> str:
    text = value.strip()
    if not text:
        raise ScanError("Enter a target URL.")
    if len(text) > 2048 or re.search(r"[\x00-\x20\x7f]", text):
        raise ScanError("URL must be shorter than 2,048 characters and contain no whitespace/control characters.")
    if "://" not in text:
        text = "https://" + text
    try:
        parsed = urlsplit(text)
    except ValueError as exc:
        raise ScanError("Invalid URL hostname.") from exc
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ScanError("Only absolute HTTP and HTTPS website URLs are supported.")
    if parsed.username is not None or parsed.password is not None:
        raise ScanError("URLs containing usernames or passwords are not supported.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ScanError("Invalid URL port.") from exc
    if port == 0:
        raise ScanError("Invalid URL port.")
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ScanError("Use an ASCII/punycode hostname and percent-encode non-ASCII URL characters.") from exc
    return text


def validate_public_target(url: str) -> str:
    url = normalize_url(url)
    host = urlsplit(url).hostname
    assert host is not None
    try:
        answers = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ScanError(f"Could not resolve target host: {host}") from exc
    addresses = {record[4][0] for record in answers}
    if not addresses:
        raise ScanError("Target host did not return an IP address.")
    if any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ScanError("Private, loopback, reserved, and local network addresses are blocked.")
    return url


def fetch_headers(url: str, timeout: float = 8.0, origin: str | None = None) -> ResponseSnapshot:
    """Request response headers only; response body is never read."""
    validate_public_target(url)
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme == "https" else 80)
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    connection: http.client.HTTPConnection | http.client.HTTPSConnection
    if parts.scheme == "https":
        connection = http.client.HTTPSConnection(
            parts.hostname, port, timeout=timeout, context=ssl.create_default_context()
        )
    else:
        connection = http.client.HTTPConnection(parts.hostname, port, timeout=timeout)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json;q=0.9,*/*;q=0.5"}
    if origin:
        headers["Origin"] = origin
    try:
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        return ResponseSnapshot(url=url, status=response.status, headers=tuple(response.getheaders()))
    except (OSError, ssl.SSLError, http.client.HTTPException, ValueError) as exc:
        raise ScanError(f"Connection failed: {exc}") from exc
    finally:
        connection.close()


def fetch_with_redirects(url: str, timeout: float = 8.0) -> tuple[ResponseSnapshot, tuple[str, ...]]:
    current = validate_public_target(url)
    redirects: list[str] = []
    original_host = urlsplit(current).hostname or ""
    for index in range(MAX_REDIRECTS + 1):
        response = fetch_headers(current, timeout=timeout)
        location = response.get("Location")
        if response.status not in (301, 302, 303, 307, 308) or not location:
            return response, tuple(redirects)
        if index >= MAX_REDIRECTS:
            raise ScanError("Target exceeded the three-redirect safety limit.")
        new_url = urljoin(current, location)
        new_host = urlsplit(new_url).hostname or ""
        # An initial authorization must not silently extend to an unrelated site.
        if new_host.removeprefix("www.").lower() != original_host.removeprefix("www.").lower():
            raise ScanError("Redirect left the authorized hostname; audit the new target separately if authorized.")
        validate_public_target(new_url)
        redirects.append(new_url)
        current = new_url
    raise ScanError("Redirect limit reached.")


def _finding(key: str, title: str, status: str, severity: str,
             detail: str, recommendation: str, evidence: str = "") -> Finding:
    return Finding(key, title, status, severity, detail, recommendation, evidence)


def assess_headers(response: ResponseSnapshot, probe: ResponseSnapshot | None = None) -> tuple[Finding, ...]:
    """Analyze supplied response metadata without any network access."""
    items: list[Finding] = []
    is_https = urlsplit(response.url).scheme == "https"

    if is_https:
        items.append(_finding("https", "HTTPS transport", "PASS", "NONE",
            "The observed response was delivered over HTTPS.", "Continue enforcing HTTPS."))
    else:
        items.append(_finding("https", "HTTPS transport", "WARN", "HIGH",
            "The observed response was delivered over unencrypted HTTP.",
            "Use HTTPS and redirect HTTP traffic to HTTPS."))

    hsts = response.get("Strict-Transport-Security")
    if not is_https:
        items.append(_finding("hsts", "HSTS policy", "INFO", "NONE",
            "HSTS is evaluated only on HTTPS responses.", "Enable HTTPS before configuring HSTS."))
    elif not hsts:
        items.append(_finding("hsts", "HSTS policy", "WARN", "MEDIUM",
            "The Strict-Transport-Security header was not observed.",
            "Consider HSTS with an appropriate max-age after verifying HTTPS readiness."))
    else:
        match = re.search(r"(?:^|;)\s*max-age\s*=\s*(\d+)\s*(?:;|$)", hsts, re.I)
        if not match or int(match.group(1)) == 0:
            items.append(_finding("hsts", "HSTS policy", "WARN", "MEDIUM",
                "The observed HSTS policy is missing an effective positive max-age.",
                "Set a positive HSTS max-age after ensuring the whole site works over HTTPS."))
        elif int(match.group(1)) < 15552000:
            items.append(_finding("hsts", "HSTS policy", "WARN", "LOW",
                "HSTS is enabled but max-age is below six months.",
                "Review whether a longer HSTS max-age is suitable for your deployment."))
        else:
            items.append(_finding("hsts", "HSTS policy", "PASS", "NONE",
                "A positive HSTS max-age of at least six months was observed.",
                "Review subdomains and preload separately if applicable."))

    csp = response.get("Content-Security-Policy")
    items.append(_finding("csp", "Content Security Policy",
        "PASS" if csp else "WARN", "NONE" if csp else "MEDIUM",
        "A CSP response header is present; individual directives have not been validated." if csp
        else "No enforced Content-Security-Policy response header was observed.",
        "Review restrictive CSP directives, including script-src and object-src, for your application."))

    nosniff = response.get("X-Content-Type-Options").strip().lower() == "nosniff"
    items.append(_finding("nosniff", "MIME sniffing protection",
        "PASS" if nosniff else "WARN", "NONE" if nosniff else "MEDIUM",
        "X-Content-Type-Options: nosniff is present." if nosniff else
        "The nosniff directive was not observed.",
        "Set X-Content-Type-Options: nosniff on applicable responses."))

    xfo = response.get("X-Frame-Options").strip().upper()
    frame_directive = re.search(r"(?:^|;)\s*frame-ancestors\s+([^;]+)", csp, re.I)
    frame_values = frame_directive.group(1).split() if frame_directive else []
    frame_ancestors = bool(frame_values) and "*" not in frame_values
    frame_guard = xfo in ("DENY", "SAMEORIGIN") or frame_ancestors
    items.append(_finding("framing", "Anti-framing control",
        "PASS" if frame_guard else "WARN", "NONE" if frame_guard else "MEDIUM",
        "An X-Frame-Options restriction or CSP frame-ancestors directive was observed." if frame_guard
        else "No supported anti-framing restriction was observed.",
        "Use CSP frame-ancestors, or X-Frame-Options where needed to protect interactive pages."))

    referrer = response.get("Referrer-Policy").strip()
    items.append(_finding("referrer", "Referrer policy",
        "PASS" if referrer else "WARN", "NONE" if referrer else "LOW",
        "A Referrer-Policy header is present; its value should be reviewed." if referrer
        else "No explicit Referrer-Policy response header was observed.",
        "Consider strict-origin-when-cross-origin or stricter based on site requirements."))

    permission = response.get("Permissions-Policy").strip()
    items.append(_finding("permissions", "Browser permissions policy",
        "PASS" if permission else "INFO", "NONE",
        "A Permissions-Policy header was observed." if permission else
        "No Permissions-Policy header was observed. This is a hardening opportunity, not proof of a vulnerability.",
        "Consider limiting browser features (camera, microphone, geolocation) when appropriate."))

    base_origin = response.get("Access-Control-Allow-Origin").strip()
    if probe is None:
        items.append(_finding("cors", "CORS origin behavior", "INFO", "NONE",
            "Origin reflection was not tested; CORS exposure is undetermined.",
            "Enable the optional harmless Origin probe for a limited CORS observation."))
    elif probe.status in (301, 302, 303, 307, 308):
        items.append(_finding("cors", "CORS origin behavior", "INFO", "NONE",
            "The Origin probe redirected, so this check is inconclusive.",
            "Verify CORS behavior in the actual application context."))
    else:
        observed = probe.get("Access-Control-Allow-Origin").strip()
        creds = probe.get("Access-Control-Allow-Credentials").strip() == "true"
        if len(probe.get_all("Access-Control-Allow-Origin")) > 1 or len(probe.get_all("Access-Control-Allow-Credentials")) > 1:
            items.append(_finding("cors", "CORS origin behavior", "WARN", "LOW",
                "Duplicate CORS response headers were observed; browser sharing cannot be inferred from the first value.",
                "Return one valid allow-origin value and, when needed, one allow-credentials value."))
        elif observed == PROBE_ORIGIN and creds:
            items.append(_finding("cors", "CORS origin behavior", "WARN", "HIGH",
                "The server echoed an arbitrary Origin and enabled credentialed sharing on this response.",
                "Use a strict trusted-origin allowlist; review endpoints containing sensitive data.",
                "Arbitrary origin reflected with Access-Control-Allow-Credentials: true"))
        elif observed == PROBE_ORIGIN:
            items.append(_finding("cors", "CORS origin behavior", "WARN", "LOW",
                "The response reflected an arbitrary Origin without credentialed access.",
                "Verify whether public cross-origin access is intended.",
                "Arbitrary origin reflected (credentials not enabled)"))
        elif observed == "*" and creds:
            items.append(_finding("cors", "CORS origin behavior", "WARN", "LOW",
                "Wildcard Origin and credentials were combined; browsers block this credentialed combination.",
                "Use an explicit trusted origin when legitimate credentialed CORS is required.",
                "ACAO: *; ACAC: true (browser rejects credentialed sharing)"))
        elif observed == "null" and creds:
            items.append(_finding("cors", "CORS origin behavior", "WARN", "MEDIUM",
                "The literal null Origin was allowed together with credentials.",
                "Treat null origins cautiously and restrict credentialed sharing to trusted origins."))
        elif observed == "*" or base_origin == "*":
            items.append(_finding("cors", "CORS origin behavior", "INFO", "NONE",
                "Wildcard CORS sharing was observed; it may be intentional for public resources.",
                "Check whether the endpoint is intended to serve public non-credentialed callers."))
        else:
            items.append(_finding("cors", "CORS origin behavior", "PASS", "NONE",
                "The arbitrary Origin was not echoed with credentialed sharing on the tested response. This is not a full CORS audit.",
                "Audit additional API endpoints and allowed origins separately if needed."))

    raw_cookies = response.get_all("Set-Cookie")
    if not raw_cookies:
        items.append(_finding("cookies", "Cookie flags", "INFO", "NONE",
            "No Set-Cookie headers were observed on this response.",
            "Review login and authenticated responses separately."))
    else:
        for cookie in raw_cookies[:20]:
            name = cookie.partition("=")[0].strip()[:60] or "(unnamed)"
            # Store cookie *names* only; never retain values.
            params = {}
            for attribute in cookie.split(";")[1:]:
                key, _, value = attribute.strip().partition("=")
                params[key.lower()] = value.strip().lower()
            missing = []
            if "secure" not in params:
                missing.append("Secure")
            if "httponly" not in params:
                missing.append("HttpOnly (may be intentional for JavaScript-readable cookies)")
            if "samesite" not in params:
                missing.append("SameSite")
            elif params["samesite"] not in {"strict", "lax", "none"}:
                missing.append("valid SameSite value (Strict, Lax or None)")
            if params.get("samesite") == "none" and "secure" not in params:
                missing.append("SameSite=None requires Secure")
            if "secure" in params and not is_https:
                missing.append("Secure cookie delivered over HTTP; public browsers will reject it")
            if missing:
                items.append(_finding("cookie-" + str(len(items)), "Cookie flags: " + name,
                    "WARN", "MEDIUM" if "Secure" in missing else "LOW",
                    "Cookie attributes need review: " + ", ".join(missing) + ".",
                    "Review Secure, HttpOnly and SameSite based on the cookie's actual purpose.",
                    "Cookie name: " + name))
            else:
                items.append(_finding("cookie-" + str(len(items)), "Cookie flags: " + name,
                    "PASS", "NONE", "Secure, HttpOnly and SameSite were observed.",
                    "Verify attribute values align with application behavior.", "Cookie name: " + name))
        if len(raw_cookies) > 20:
            items.append(_finding("cookie-limit", "Cookie review limit", "INFO", "NONE",
                "Only the first 20 Set-Cookie headers were reviewed.",
                "Inspect remaining cookies separately."))
    return tuple(items)


def build_result(target_url: str, snapshot: ResponseSnapshot,
                 probe: ResponseSnapshot | None = None, redirects: Iterable[str] = (),
                 elapsed_ms: int = 0, demo: bool = False) -> AuditResult:
    findings = assess_headers(snapshot, probe)
    penalty = {"HIGH": 17, "MEDIUM": 10, "LOW": 5}
    score = max(0, 100 - sum(penalty.get(f.severity, 0) for f in findings if f.status == "WARN"))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    return AuditResult(target_url=target_url, final_url=snapshot.url,
        scanned_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        http_status=snapshot.status, score=score, grade=grade,
        findings=findings, redirects=tuple(redirects), elapsed_ms=elapsed_ms, demo=demo)


def scan(url: str, test_cors: bool = True, timeout: float = 8.0) -> AuditResult:
    """Perform a limited, passive review only of an authorized URL."""
    if not 0 < timeout <= 30:
        raise ScanError("Timeout must be greater than zero and at most 30 seconds.")
    target = validate_public_target(url)
    start = time.monotonic()
    response, redirects = fetch_with_redirects(target, timeout=timeout)
    probe = None
    if test_cors:
        try:
            probe = fetch_headers(response.url, timeout=timeout, origin=PROBE_ORIGIN)
        except ScanError:
            # An unsuccessful optional probe does not invalidate the basic header audit.
            probe = None
    elapsed = round((time.monotonic() - start) * 1000)
    return build_result(target, response, probe, redirects=redirects, elapsed_ms=elapsed)


def demo_result() -> AuditResult:
    """Offline, intentionally misconfigured example; not real scan findings."""
    url = "https://demo.example/"
    response = ResponseSnapshot(url=url, status=200, headers=(
        ("Content-Type", "text/html"),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ("Set-Cookie", "demo_session=REDACTED; Path=/; SameSite=Lax"),
    ))
    probe = ResponseSnapshot(url=url, status=200, headers=(
        ("Access-Control-Allow-Origin", PROBE_ORIGIN),
        ("Access-Control-Allow-Credentials", "true"),
    ))
    return build_result(url, response, probe, elapsed_ms=0, demo=True)
