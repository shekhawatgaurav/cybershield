# Verification record

Local verification on 19 October 2026, Windows, Python 3.14.7, Streamlit 1.66.0.

- Original baseline: 13 offline scanner tests passed before changes.
- Updated suite: 27 scanner/CLI tests passed; 2 Streamlit AppTest cases passed after correcting the test script paths (29 total).
- Python syntax compilation passed for both apps, scanner modules, tests and fixture generation.
- Dependency consistency: `pip check` reported no broken requirements.
- JavaScript syntax: `node --check` passed for `docs/app.js` and `docs/demo-data.js`.
- Streamlit startup: loopback server started; `/_stcore/health` returned HTTP 200.
- Static startup: local HTTP server returned HTTP 200.
- Headless Microsoft Edge browser checks passed: baseline score/counts, improved scenario, header filtering, empty-filter state, JSON download content and internal anchor targets.
- Responsive checks passed at 320, 390, 430, 768, 1024 and 1440 pixels with no document-level horizontal overflow. Header tables can scroll within their containers.
- Browser reported no JavaScript exceptions or external network requests during demo interaction.
- Desktop and mobile screenshots are in `docs/assets/`.

The first dashboard test run failed because relative AppTest paths resolved within `tests/`. Tests now use absolute paths derived from their file location; both passed on rerun. No application failure was hidden.

No live security scans were performed. DNS, HTTP and CORS test targets are mocked; results do not establish coverage of all browsers, websites or security threats. Streamlit dependencies and temporary browser tooling are installed only locally and are not committed. Browser tooling is not a runtime project dependency.

GitHub CI and Pages deployment status must be assessed on the actual published commit, independently of these local checks.

## Dashboard upgrade verification

The updated cobalt/navy interface was checked in Microsoft Edge on 19 October 2026. Browser checks passed for both guided demo scenarios, header search and its empty state, JSON/HTML/CSV download contents, and the Print/PDF button invoking browser printing. Duplicate element IDs were checked. Responsive checks passed at all six existing viewport widths. Desktop and mobile screenshots were refreshed. No Python engine changes or new runtime dependencies were introduced.

## Light-theme redesign verification

The original light-themed landing page and audit workspace were verified in Microsoft Edge on 19 October 2026. The earlier cobalt/navy design is superseded. All existing demo interactions and JSON/HTML/CSV exports passed. Checks also passed for six viewport widths (320, 390, 430, 768, 1024 and 1440 pixels), internal anchors, unique IDs, requested section counts, keyboard-operated FAQs, the light color scheme, audit-only print layout and no-JavaScript information fallback. No JavaScript errors or external runtime requests were observed. A mobile overflow discovered during development was corrected before publishing. Screenshots cover both the landing page and audit workspace. No Python engine changes or runtime dependencies were added.

## Fictional website fixtures

On 20 October 2026, browser checks passed for Northstar Store and Orbit Docs in both baseline and improved configurations: scores match Python-generated data, target labels and JSON exports match the selected site, both store cookies render, the no-cookie portal observation renders, and no cookie values appear in exports. Demo execution and 320/390/768/1440px overflow checks passed. The existing export/search/demo regression checks also passed. These fixtures are fictional `.example` domains and send no target requests.
