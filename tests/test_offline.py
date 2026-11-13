import contextlib, io, os, sys, unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import cardmarket_monitor as m

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.guard=patch.object(m.requests.sessions.Session,"request",side_effect=AssertionError("Network forbidden in offline tests"))
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def offer(self,**kw):
        values=dict(seller_name="Synthetic",seller_profile_url="https://example.invalid/seller",seller_country="ES",seller_sales=500,seller_is_professional=False,quantity=2,price=Decimal("0.10"))
        values.update(kw);return m.Offer(**values)

    def test_euro_price(self):
        for value, expected in [("0,10 €","0.10"),("1.234,56 €","1234.56"),("0,02 €","0.02")]:
            self.assertEqual(m.parse_price(value),Decimal(expected))
    def test_row_text_is_not_a_price(self):
        self.assertIsNone(m.parse_price("Vendedor 500 2 0,10 €"))
    def test_country_filter(self):
        self.assertFalse(m.competitor_is_valid(self.offer(seller_country="FR"),2,100,300))
    def test_quantity_filter(self):
        self.assertFalse(m.competitor_is_valid(self.offer(quantity=1),2,100,300))
    def test_relative_threshold_preserved(self):
        self.assertFalse(m.competitor_is_valid(self.offer(seller_sales=399),2,100,300))
        self.assertTrue(m.competitor_is_valid(self.offer(seller_sales=400),2,100,300))
    def test_professional_threshold_preserved(self):
        self.assertFalse(m.competitor_is_valid(self.offer(seller_is_professional=True,seller_sales=100),2,100,300))
        self.assertTrue(m.competitor_is_valid(self.offer(seller_is_professional=True,seller_sales=101),2,100,300))
    def test_price_floor(self):
        l=m.Listing("Synthetic","https://example.invalid/card",2,Decimal("0.10"))
        f=m.analyze_listing(l,[self.offer(price=Decimal("0.02"))],min_price=Decimal("0.02"),our_sales=100,non_pro_extra_sales=300)
        self.assertEqual(f.suggested_price,Decimal("0.02"))
    @unittest.expectedFailure
    def test_known_parser_gap_requires_verified_html_contract(self):
        # Semantic table fixture only. It does NOT assert the live provider DOM.
        html='<table><tbody><tr><td><a href="/Users/Synthetic">Vendedor</a></td><td class="sales">500</td><td class="quantity">2</td><td class="price">0,10 €</td><td><span class="country" title="ES"></span></td></tr></tbody></table>'
        offers=m.parse_offers(html)
        self.assertEqual(len(offers),1)
        self.assertEqual((offers[0].seller_sales,offers[0].quantity,offers[0].price),(500,2,Decimal("0.10")))

    def exercise(self,responses,profiles=2,listings=None):
        env={"CARDMARKET_USERNAME":"SYNTHETIC","PROFILE_URLS":",".join("https://example.invalid/"+str(i) for i in range(profiles)),"USE_CLOUDSCRAPER":"false","EMAIL_ENABLED":"false","WEBHOOK_ENABLED":"false"}
        output=io.StringIO()
        original_inspect = m.inspect_page
        def inspected(html, kind):
            if kind == 'profile' and listings is not None:
                # A synthetic adapter double, never evidence about live HTML.
                return m.ParseResult(listings, 'READY', len(listings), 0, 'Synthetic test adapter')
            return original_inspect(html, kind)
        listing_patch = patch.object(m,"inspect_page",side_effect=inspected)
        with listing_patch,patch.dict(os.environ,env,clear=True),patch.object(m,"load_dotenv"),patch.object(m,"load_ignored_cards",return_value=set()),patch.object(m,"create_http_session",return_value=object()),patch.object(m,"get_html",side_effect=responses),patch.object(m,"send_email",side_effect=AssertionError("mail forbidden")),patch.object(m,"send_webhook",side_effect=AssertionError("webhook forbidden")),contextlib.redirect_stdout(output):
            code=m.run("synthetic-unused.env","synthetic-unused.txt")
        return code,output.getvalue()
    def test_total_profile_failure_is_not_success(self):
        code,report=self.exercise([m.requests.RequestException("synthetic"),m.requests.RequestException("synthetic")])
        self.assertNotEqual(code,0)
        self.assertIn("fallida",report.lower())
        self.assertNotIn("No se detectaron",report)
    def test_partial_failure_is_reported(self):
        code,report=self.exercise(["<html></html>",m.requests.RequestException("synthetic")])
        self.assertNotEqual(code,0)
        self.assertIn("incompleta",report.lower())
        self.assertIn("1/2",report)
    def test_received_unknown_pages_are_not_confirmed_empty(self):
        code,report=self.exercise(["<html></html>","<html></html>"])
        self.assertEqual(code,2)
        self.assertIn("2/2",report)
        self.assertIn("HTML desconocido: 2",report)
        self.assertNotIn("No se detectaron",report)
    def test_article_failure_is_incomplete(self):
        listing=m.Listing("Synthetic","https://example.invalid/card",2,Decimal("0.10"))
        code,report=self.exercise(["<html></html>",m.requests.RequestException("synthetic")],profiles=1,listings=[listing])
        self.assertEqual(code,1)
        self.assertIn("incompleta",report.lower())
        self.assertIn("Artículos leídos: 0/1",report)
        self.assertNotIn("No se detectaron",report)
    def test_article_coverage_counts_successful_response(self):
        listing=m.Listing("Synthetic","https://example.invalid/card",2,Decimal("0.10"))
        code,report=self.exercise(["<html></html>","<html></html>"],profiles=1,listings=[listing])
        self.assertEqual(code,2)
        self.assertIn("Artículos leídos: 1/1",report)
        self.assertIn("Artículos interpretados: 0/1",report)
    def test_missing_configuration_fails_before_network(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,"load_dotenv"):
            with self.assertRaisesRegex(ValueError,"CARDMARKET_USERNAME"):
                m.run("synthetic-unused.env","synthetic-unused.txt")
if __name__=="__main__":unittest.main(verbosity=2)

