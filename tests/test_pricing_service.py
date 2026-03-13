import unittest

from src.models import CartItem
from src.pricing import PricingService, PricingError


class TestPricingService(unittest.TestCase):
    def setUp(self):
        self.pricing_service = PricingService()

    def test_subtotal_cents_success(self):
        items = [CartItem(sku=0, unit_price_cents=1, qty=1)]
        subtotal_cents = self.pricing_service.subtotal_cents(items)

        self.assertEqual(subtotal_cents, 1)

    def test_subtotal_cents_invalid_qty(self):
        items = [CartItem(sku=0, unit_price_cents=1, qty=0)]
        with self.assertRaises(PricingError) as context:
            self.pricing_service.subtotal_cents(items)

        self.assertEqual(str(context.exception), "qty must be > 0")

    def test_subtotal_cents_invalid_unit_price_cents(self):
        items = [CartItem(sku=0, unit_price_cents=-1, qty=1)]
        with self.assertRaises(PricingError) as context:
            self.pricing_service.subtotal_cents(items)

        self.assertEqual(str(context.exception), "unit_price_cents must be >= 0")

    def test_apply_coupon_no_coupon_success(self):
        subtotal = self.pricing_service.apply_coupon(subtotal=1, coupon_code=None)

        self.assertEqual(subtotal, 1)

    def test_apply_coupon_pct_success(self):
        subtotal = self.pricing_service.apply_coupon(subtotal=100, coupon_code="SAVE10")

        self.assertEqual(subtotal, 90)

    def test_apply_coupon_abs_success(self):
        subtotal = self.pricing_service.apply_coupon(subtotal=3000, coupon_code="CLP2000")

        self.assertEqual(subtotal, 1000)

    def test_apply_coupon_invalid_coupon(self):
        with self.assertRaises(PricingError) as context:
            self.pricing_service.apply_coupon(subtotal=1, coupon_code="INVALID")

        self.assertEqual(str(context.exception), "invalid coupon")

    def test_tax_cents_success_cl(self):
        tax = self.pricing_service.tax_cents(net_subtotal=100, country="CL")

        self.assertEqual(tax, 19)

    def test_tax_cents_success_us(self):
        tax = self.pricing_service.tax_cents(net_subtotal=100, country="US")

        self.assertEqual(tax, 0)

    def test_tax_cents_success_eu(self):
        tax = self.pricing_service.tax_cents(net_subtotal=100, country="EU")

        self.assertEqual(tax, 21)

    def test_tax_cents_unsupported_country(self):
        with self.assertRaises(PricingError) as context:
            self.pricing_service.tax_cents(net_subtotal=100, country="AR")

        self.assertEqual(str(context.exception), "unsupported country")

    def test_shipping_cents_success_cl(self):
        shipping_cents = self.pricing_service.shipping_cents(net_subtotal=20000, country="CL")

        self.assertEqual(shipping_cents, 0)

    def test_shipping_cents_success_us(self):
        shipping_cents = self.pricing_service.shipping_cents(net_subtotal=20000, country="US")

        self.assertEqual(shipping_cents, 5000)

    def test_shipping_cents_unsupported_country(self):
        with self.assertRaises(PricingError) as context:
            self.pricing_service.shipping_cents(net_subtotal=100, country="AR")

        self.assertEqual(str(context.exception), "unsupported country")

    def test_total_cents_success(self):
        items = [CartItem(sku=0, unit_price_cents=0, qty=1)]
        total_cents = self.pricing_service.total_cents(items, coupon_code=None, country="US")

        self.assertEqual(total_cents, 5000)