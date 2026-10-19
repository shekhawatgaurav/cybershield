"""Offline regression tests for observed audit and export failures."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cybershield.cli import main
from cybershield.scanner import (
    PROBE_ORIGIN, ResponseSnapshot, ScanError, assess_headers,
    fetch_with_redirects, normalize_url, scan,
)


class RegressionTests(unittest.TestCase):
    def finding(self, key, headers, url="https://example.com"):
        return next(f for f in assess_headers(ResponseSnapshot(url, 200, tuple(headers))) if f.key.startswith(key))

    def test_invalid_urls_have_useful_errors(self):
        for url in ("https://[bad", "https://example.com:bad", "https://example.com:0", "https://example.com/café"):
            with self.subTest(url=url), self.assertRaises(ScanError):
                normalize_url(url)

    def test_hsts_invalid_suffix_does_not_pass(self):
        finding = self.finding("hsts", [("Strict-Transport-Security", "max-age=31536000garbage")])
        self.assertEqual(finding.status, "WARN")

    def test_http_cookie_without_secure_does_not_pass(self):
        f = self.finding("cookie-", [("Set-Cookie", "sid=secret; HttpOnly; SameSite=Lax")], "http://example.com")
        self.assertEqual(f.severity, "MEDIUM")
        self.assertIn("Secure", f.detail)

    def test_invalid_samesite_is_flagged(self):
        f = self.finding("cookie-", [("Set-Cookie", "sid=secret; Secure; HttpOnly; SameSite=invalid")])
        self.assertEqual(f.status, "WARN")

    def test_samesite_none_requires_secure(self):
        f = self.finding("cookie-", [("Set-Cookie", "sid=secret; HttpOnly; SameSite=None")])
        self.assertIn("SameSite=None requires Secure", f.detail)

    def test_secure_cookie_over_http_is_not_pass(self):
        f = self.finding("cookie-", [("Set-Cookie", "sid=secret; Secure; HttpOnly; SameSite=Lax")], "http://example.com")
        self.assertEqual(f.status, "WARN")

    def test_cors_credentials_are_case_sensitive(self):
        base = ResponseSnapshot("https://example.com", 200, ())
        probe = ResponseSnapshot(base.url, 200, (("Access-Control-Allow-Origin", PROBE_ORIGIN), ("Access-Control-Allow-Credentials", "TRUE")))
        f = next(f for f in assess_headers(base, probe) if f.key == "cors")
        self.assertEqual(f.severity, "LOW")

    def test_duplicate_cors_headers_do_not_claim_credentialed_sharing(self):
        base = ResponseSnapshot("https://example.com", 200, ())
        probe = ResponseSnapshot(base.url, 200, (("Access-Control-Allow-Origin", PROBE_ORIGIN), ("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Credentials", "true")))
        f = next(f for f in assess_headers(base, probe) if f.key == "cors")
        self.assertEqual(f.severity, "LOW")
        self.assertIn("Duplicate", f.detail)

    def test_redirect_request_limit(self):
        response = ResponseSnapshot("https://example.com", 302, (("Location", "/again"),))
        with patch("cybershield.scanner.validate_public_target", side_effect=lambda url: url), patch("cybershield.scanner.fetch_headers", return_value=response) as fetch:
            with self.assertRaisesRegex(ScanError, "three-redirect"):
                fetch_with_redirects(response.url)
            self.assertEqual(fetch.call_count, 4)

    def test_skip_cors_sends_no_probe(self):
        response = ResponseSnapshot("https://example.com", 200, ())
        with patch("cybershield.scanner.validate_public_target", side_effect=lambda url: url), patch("cybershield.scanner.fetch_with_redirects", return_value=(response, ())), patch("cybershield.scanner.fetch_headers") as fetch:
            scan(response.url, test_cors=False)
            fetch.assert_not_called()

    def test_timeout_validation_before_network(self):
        with patch("cybershield.scanner.validate_public_target") as validate:
            with self.assertRaises(ScanError):
                scan("https://example.com", timeout=0)
            validate.assert_not_called()

    def test_cli_requires_authorization_before_scan(self):
        with patch("cybershield.cli.scan") as run, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                main(["--url", "https://example.com"])
            self.assertEqual(exc.exception.code, 2)
            run.assert_not_called()

    def test_cli_offline_json_export(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            path = Path(folder) / "report.json"
            self.assertEqual(main(["--demo", "--format", "json", "--output", str(path)]), 0)
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["demo"])

    def test_cli_connection_error_returns_two(self):
        with patch("cybershield.cli.scan", side_effect=ScanError("connection failed")), contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(main(["--url", "https://example.com", "--authorized"]), 2)
            self.assertIn("connection failed", output.getvalue())
