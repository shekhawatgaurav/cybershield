"""All tests run offline; no third-party dependencies or target traffic."""
import unittest
from unittest.mock import patch
from cybershield.scanner import (
    PROBE_ORIGIN, ResponseSnapshot, ScanError, assess_headers, build_result,
    demo_result, normalize_url, validate_public_target, fetch_with_redirects, scan,
)
from cybershield.reports import to_html, to_json


class ScannerTests(unittest.TestCase):
    def test_url_validation(self):
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        with self.assertRaises(ScanError):
            normalize_url("file:///etc/passwd")
        with self.assertRaises(ScanError):
            normalize_url("https://user:pass@example.com")
        with self.assertRaises(ScanError):
            normalize_url("https://example.com/\nInjected: x")

    def test_private_ip_blocked(self):
        with patch("cybershield.scanner.socket.getaddrinfo", return_value=[
            (2, 1, 6, "", ("127.0.0.1", 0))
        ]):
            with self.assertRaisesRegex(ScanError, "Private"):
                validate_public_target("http://test.example")

    def test_public_ip_accepted(self):
        with patch("cybershield.scanner.socket.getaddrinfo", return_value=[
            (2, 1, 6, "", ("93.184.215.14", 0))
        ]):
            self.assertEqual(validate_public_target("https://example.com"), "https://example.com")

    def test_strong_configuration(self):
        headers = (("Strict-Transport-Security", "max-age=31536000"),
            ("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'"),
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
            ("Permissions-Policy", "camera=()"),
            ("Set-Cookie", "sid=SECRET; Secure; HttpOnly; SameSite=Lax"))
        response = ResponseSnapshot("https://example.com", 200, headers)
        probe = ResponseSnapshot("https://example.com", 200, ())
        result = build_result("https://example.com", response, probe)
        self.assertEqual(result.score, 100)
        self.assertFalse(any(f.status == "WARN" for f in result.findings))

    def test_credentialed_arbitrary_origin_reflection_is_high(self):
        base = ResponseSnapshot("https://example.com", 200, ())
        probe = ResponseSnapshot("https://example.com", 200,
            (("Access-Control-Allow-Origin", PROBE_ORIGIN),
             ("Access-Control-Allow-Credentials", "true")))
        cors = next(f for f in assess_headers(base, probe) if f.key == "cors")
        self.assertEqual((cors.status, cors.severity), ("WARN", "HIGH"))

    def test_wildcard_credentials_not_false_exploit(self):
        base = ResponseSnapshot("https://example.com", 200, ())
        probe = ResponseSnapshot("https://example.com", 200,
            (("Access-Control-Allow-Origin", "*"),
             ("Access-Control-Allow-Credentials", "true")))
        cors = next(f for f in assess_headers(base, probe) if f.key == "cors")
        self.assertNotEqual(cors.severity, "HIGH")
        self.assertIn("browsers block", cors.detail)

    def test_cookie_values_not_in_exports(self):
        result = build_result("https://example.com", ResponseSnapshot(
            "https://example.com", 200,
            (("Set-Cookie", "session=TOP_SECRET_TOKEN; SameSite=Lax"),)))
        self.assertNotIn("TOP_SECRET_TOKEN", to_json(result))
        self.assertNotIn("TOP_SECRET_TOKEN", to_html(result))
        self.assertIn("session", to_html(result))

    def test_html_escapes_untrusted_target(self):
        target = "https://example.com/a?q=<script>alert(1)</script>"
        result = build_result(target, ResponseSnapshot(target, 200, ()))
        page = to_html(result)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_wildcard_frame_ancestors_is_not_protection(self):
        response = ResponseSnapshot("https://example.com", 200,
            (("Content-Security-Policy", "frame-ancestors *"),))
        framing = next(f for f in assess_headers(response) if f.key == "framing")
        self.assertEqual(framing.status, "WARN")

    def test_unrelated_redirect_is_blocked(self):
        response = ResponseSnapshot("https://example.com", 302,
            (("Location", "https://unrelated.test/"),))
        with patch("cybershield.scanner.validate_public_target", side_effect=lambda url: url), \
             patch("cybershield.scanner.fetch_headers", return_value=response):
            with self.assertRaisesRegex(ScanError, "authorized hostname"):
                fetch_with_redirects("https://example.com")

    def test_scan_sends_optional_origin_probe(self):
        response = ResponseSnapshot("https://example.com", 200, ())
        probe = ResponseSnapshot("https://example.com", 200,
            (("Access-Control-Allow-Origin", PROBE_ORIGIN),))
        with patch("cybershield.scanner.validate_public_target", side_effect=lambda url: url), \
             patch("cybershield.scanner.fetch_with_redirects", return_value=(response, ())), \
             patch("cybershield.scanner.fetch_headers", return_value=probe) as fn:
            result = scan("https://example.com")
            fn.assert_called_once_with("https://example.com", timeout=8.0, origin=PROBE_ORIGIN)
            self.assertEqual(result.final_url, "https://example.com")

    def test_optional_probe_failure_leaves_base_audit(self):
        response = ResponseSnapshot("https://example.com", 200, ())
        with patch("cybershield.scanner.validate_public_target", side_effect=lambda url: url), \
             patch("cybershield.scanner.fetch_with_redirects", return_value=(response, ())), \
             patch("cybershield.scanner.fetch_headers", side_effect=ScanError("probe failed")):
            result = scan("https://example.com")
            cors = next(f for f in result.findings if f.key == "cors")
            self.assertEqual(cors.status, "INFO")

    def test_demo_is_labelled(self):
        result = demo_result()
        self.assertTrue(result.demo)
        self.assertIn("SIMULATED", to_html(result))
        self.assertGreater(result.to_dict()["summary"]["warnings"], 0)


if __name__ == "__main__":
    unittest.main()
