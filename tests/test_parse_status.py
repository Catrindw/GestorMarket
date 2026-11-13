"""Synthetic coverage contracts, not fixtures of the provider's HTML."""
import contextlib
from dataclasses import replace
import hashlib
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import cardmarket_monitor as m


class ParseStatusTests(unittest.TestCase):
    HTML = '<html><body>synthetic coverage fixture</body></html>'

    def setUp(self):
        guard = patch.object(m.requests.sessions.Session, 'request', side_effect=AssertionError('Network forbidden'))
        guard.start(); self.addCleanup(guard.stop)
        for name in ['send_email', 'send_webhook']:
            guard = patch.object(m, name, side_effect=AssertionError('Notifications forbidden'))
            guard.start(); self.addCleanup(guard.stop)

    def evidence(self, **changes):
        evidence = m.ReviewedPageEvidence('synthetic-test-contract-only', hashlib.sha256(self.HTML.encode()).hexdigest(), 1, True, True)
        return replace(evidence, **changes)

    def test_no_rows_without_evidence_is_unknown(self):
        self.assertEqual(m.classify_parse(self.HTML, [], 0).status, 'UNKNOWN_HTML')

    def test_candidate_rows_without_parsed_items_are_partial(self):
        result = m.classify_parse(self.HTML, [], 2)
        self.assertEqual((result.status, result.skipped_rows, result.complete), ('PARTIAL', 2, False))

    def test_nonempty_heuristic_is_still_unverified(self):
        self.assertEqual(m.classify_parse(self.HTML, ['synthetic row'], 1).status, 'PARTIAL')

    def test_validated_nonempty_contract(self):
        self.assertTrue(m.classify_parse(self.HTML, ['synthetic row'], 1, self.evidence()).complete)

    def test_confirmed_empty_requires_explicit_evidence(self):
        result = m.classify_parse(self.HTML, [], 0, self.evidence(expected_rows=0, empty_confirmed=True))
        self.assertEqual(result.status, 'EMPTY_CONFIRMED')
        self.assertTrue(result.complete)

    def test_zero_expected_does_not_implicitly_mean_empty(self):
        self.assertEqual(m.classify_parse(self.HTML, [], 0, self.evidence(expected_rows=0)).status, 'UNKNOWN_HTML')

    def test_evidence_for_other_response_is_rejected(self):
        self.assertFalse(m.classify_parse(self.HTML + ' changed', ['row'], 1, self.evidence()).complete)

    def test_empty_contract_id_is_not_evidence(self):
        self.assertFalse(m.classify_parse(self.HTML, ['row'], 1, self.evidence(contract_id=' ')).complete)

    def test_invalid_expected_counts_are_not_evidence(self):
        for count in [True, -1, '1', 1.0]:
            with self.subTest(count=count):
                self.assertFalse(m.classify_parse(self.HTML, ['row'], 1, self.evidence(expected_rows=count)).complete)

    def test_fields_not_validated(self):
        self.assertFalse(m.classify_parse(self.HTML, ['row'], 1, self.evidence(fields_validated=False)).complete)

    def test_pagination_not_complete(self):
        self.assertFalse(m.classify_parse(self.HTML, ['row'], 1, self.evidence(pagination_complete=False)).complete)

    def test_missing_parsed_row_is_partial(self):
        self.assertEqual(m.classify_parse(self.HTML, ['row'], 2, self.evidence(expected_rows=2)).status, 'PARTIAL')

    def test_unseen_expected_rows_are_partial(self):
        self.assertEqual(m.classify_parse(self.HTML, ['row'], 1, self.evidence(expected_rows=2)).status, 'PARTIAL')

    def test_empty_assertion_cannot_hide_rows(self):
        self.assertFalse(m.classify_parse(self.HTML, ['row'], 1, self.evidence(empty_confirmed=True)).complete)

    def test_html_cannot_self_certify_empty(self):
        for html in ['', '<html></html>', '<p>No offers</p>', '<div data-status="EMPTY_CONFIRMED" data-reviewed="true"></div>', '<form><input type="password"></form>']:
            with self.subTest(html=html):
                self.assertEqual(m.inspect_page(html, 'offers').status, 'UNKNOWN_HTML')

    def test_old_offer_parser_gap_is_visible_as_partial(self):
        html = '<table><tbody><tr><td><a href="/Users/Synthetic">Seller</a></td><td>500</td><td>2</td><td>0,10 €</td></tr></tbody></table>'
        result = m.inspect_page(html, 'offers')
        self.assertEqual((result.status, result.candidate_rows, result.skipped_rows), ('PARTIAL', 1, 1))

    def test_mixed_profile_rows_have_partial_coverage(self):
        html = '<table><tbody><tr><td><a href="/Products/Synthetic1">Synthetic1</a></td><td>2</td><td>0,10 €</td></tr><tr><td><a href="/Products/Synthetic2">Synthetic2</a></td><td>missing price</td></tr></tbody></table>'
        result = m.inspect_page(html, 'profile')
        self.assertEqual((result.status, result.candidate_rows, result.skipped_rows), ('PARTIAL', 2, 1))

    def test_arbitrary_table_is_not_a_known_listing(self):
        self.assertEqual(m.inspect_page('<table><tbody><tr><td>0</td></tr></tbody></table>', 'profile').status, 'UNKNOWN_HTML')

    def test_invalid_page_kind(self):
        with self.assertRaises(ValueError): m.inspect_page(self.HTML, 'invented')

    def execute(self, html, result=None):
        env = {'CARDMARKET_USERNAME':'SYNTHETIC', 'PROFILE_URLS':'https://example.invalid/profile', 'USE_CLOUDSCRAPER':'false', 'EMAIL_ENABLED':'false', 'WEBHOOK_ENABLED':'false'}
        output = io.StringIO()
        inspector = patch.object(m, 'inspect_page', return_value=result) if result else contextlib.nullcontext()
        with inspector, patch.dict(os.environ, env, clear=True), patch.object(m,'load_dotenv'), patch.object(m,'load_ignored_cards',return_value=set()), patch.object(m,'create_http_session',return_value=object()), patch.object(m,'get_html',return_value=html) as fetch, patch.object(m,'analyze_listing',side_effect=AssertionError('Unverified rows must not be analyzed')), contextlib.redirect_stdout(output):
            code = m.run('synthetic-unused.env', 'synthetic-unused.txt')
        self.assertEqual(fetch.call_count, 1)
        return code, output.getvalue()

    def test_unknown_page_does_not_become_no_findings(self):
        code, report = self.execute(self.HTML)
        self.assertEqual(code, 2)
        self.assertIn('HTML desconocido: 1', report)
        self.assertNotIn('No se detectaron', report)

    def test_partial_profile_does_not_launch_article_queries(self):
        code, report = self.execute('<table><tbody><tr><td><a href="/Products/Synthetic">Synthetic</a></td><td>2</td><td>0,10 €</td></tr></tbody></table>')
        self.assertEqual(code, 2)
        self.assertIn('Interpretación parcial: 1', report)
        self.assertIn('Artículos leídos: 0/0', report)

    def test_verified_empty_is_distinct_from_unknown(self):
        result = m.classify_parse(self.HTML, [], 0, self.evidence(expected_rows=0, empty_confirmed=True))
        code, report = self.execute(self.HTML, result)
        self.assertEqual(code, 0)
        self.assertIn('Listados vacíos acreditados: 1', report)
        self.assertIn('Perfiles interpretados: 1/1', report)

    def test_403_is_query_failure_and_never_empty(self):
        response = Mock(status_code=403)
        session = Mock(); session.get.return_value = response
        with self.assertRaises(m.requests.HTTPError) as caught:
            m.get_html(session, 'https://example.invalid/profile', 5)
        self.assertNotIn('CARDMARKET_COOKIE', str(caught.exception))
        self.assertIn('Consulta fallida', str(caught.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
