from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from myapp.models import User


@override_settings(SECURE_SSL_REDIRECT=False, STRIPE_CHECKOUT_ENABLED=False)
class StripeCheckoutAvailabilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            email="stripe-disabled-customer@example.invalid",
            password="CustomerPass123!",
            role="Customer",
        )
        self.client.force_authenticate(user=self.customer)

    def test_stripe_checkout_is_disabled_before_cart_validation(self):
        response = self.client.post(
            "/payment/create-checkout-session/",
            {"address": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 410)
        self.assertIn("WhatsApp", response.data["message"])
