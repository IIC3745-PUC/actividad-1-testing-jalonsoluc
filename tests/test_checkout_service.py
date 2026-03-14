import unittest
from unittest.mock import Mock

from src.models import CartItem
from src.pricing import PricingError
from src.checkout import CheckoutService, ChargeResult


class TestCheckoutService(unittest.TestCase):
    def setUp(self):
        self.payments = Mock()
        self.email = Mock()
        self.fraud = Mock()
        self.repo = Mock()
        self.pricing = Mock()

        self.checkout_service = CheckoutService(
            payments=self.payments,
            email=self.email,
            fraud=self.fraud,
            repo=self.repo,
            pricing=self.pricing,
        )

    def test_checkout_success(self):
        self.pricing.total_cents.return_value = 100
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(ok=True, charge_id="ch_123")

        result = self.checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=0, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.repo.save.assert_called_once()
        saved_order = self.repo.save.call_args[0][0]

        self.assertTrue(result.startswith("OK:"))

        returned_order_id = result.split("OK:")[1]
        self.assertEqual(saved_order.order_id, returned_order_id)
        self.assertEqual(saved_order.user_id, "user")
        self.assertEqual(saved_order.total_cents, 100)
        self.assertEqual(saved_order.payment_charge_id, "ch_123")
        self.assertEqual(saved_order.coupon_code, None)
        self.assertEqual(saved_order.country, "CL")

        self.email.send_receipt.assert_called_once_with("user", returned_order_id, 100)

    def test_checkout_success_unknown_charge_id(self):
        self.pricing.total_cents.return_value = 100
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(ok=True, charge_id=None)

        result = self.checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=0, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.assertTrue(result.startswith("OK:"))
        saved_order = self.repo.save.call_args[0][0]
        self.assertEqual(saved_order.payment_charge_id, "UNKNOWN")

    def test_checkout_init_without_pricing_uses_default_pricing_service(self):
        checkout_service = CheckoutService(
            payments=self.payments,
            email=self.email,
            fraud=self.fraud,
            repo=self.repo,
        )

        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(ok=True, charge_id="ch_123")

        result = checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=100, qty=1)],
            payment_token="token",
            country="US",
            coupon_code=None,
        )

        self.assertTrue(result.startswith("OK:"))
        self.repo.save.assert_called_once()

    def test_checkout_invalid_user(self):
        result = self.checkout_service.checkout(
            user_id="",
            items=[CartItem(sku=0, unit_price_cents=0, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.assertEqual(result, "INVALID_USER")

    def test_checkout_invalid_cart(self):
        self.pricing.total_cents.side_effect = PricingError(
            "unit_price_cents must be >= 0"
        )

        result = self.checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=-1, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.assertEqual(result, "INVALID_CART:unit_price_cents must be >= 0")

    def test_checkout_rejected_fraud(self):
        self.fraud.score.return_value = 80

        result = self.checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=-1, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.assertEqual(result, "REJECTED_FRAUD")

    def test_checkout_paymenet_failed(self):
        self.pricing.total_cents.return_value = 100
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(
            ok=False, charge_id="ch_123", reason="test"
        )

        result = self.checkout_service.checkout(
            user_id="user",
            items=[CartItem(sku=0, unit_price_cents=-1, qty=1)],
            payment_token="token",
            country="CL",
            coupon_code=None,
        )

        self.assertEqual(result, "PAYMENT_FAILED:test")
