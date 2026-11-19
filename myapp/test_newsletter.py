from django.test import TestCase
from rest_framework.test import APIClient

from .models import NewsletterSubscription


class NewsletterSignupTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_requires_explicit_consent(self):
        response = self.client.post(
            "/newsletter/",
            {"email": "reader@example.com", "consent": False},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(NewsletterSubscription.objects.count(), 0)

    def test_signup_saves_normalized_email_once(self):
        payload = {"email": "  Reader@Example.com ", "consent": True}

        first = self.client.post("/newsletter/", payload, format="json")
        second = self.client.post("/newsletter/", payload, format="json")

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(NewsletterSubscription.objects.count(), 1)
        self.assertTrue(NewsletterSubscription.objects.get().is_active)

    def test_signup_rejects_invalid_email(self):
        response = self.client.post(
            "/newsletter/",
            {"email": "not-an-email", "consent": True},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(NewsletterSubscription.objects.count(), 0)
