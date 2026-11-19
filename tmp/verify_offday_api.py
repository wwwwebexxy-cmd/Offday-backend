import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
import django
django.setup()
from django.db import transaction
from rest_framework.test import APIClient
from myapp.models import NewsletterSubscription

client = APIClient()
request_args = {"HTTP_HOST": "127.0.0.1"}
home = client.get("/homepage/", **request_args)
print("Homepage status:", home.status_code)
print("Homepage response type:", type(home).__name__)
if home.status_code != 200:
    print("Homepage response:", getattr(home, "content", b"").decode("utf-8", errors="replace")[:300])
else:
    print("Homepage collections:", ", ".join(item["name"] for item in home.data["categories"]))
    drops = next(item for item in home.data["categories"] if item["name"] == "OFFDAY DROPS")
    products = client.get(f"/category-products/{drops['id']}/?page_size=12", **request_args)
    print("Drops status:", products.status_code)
    print("Drops products:", ", ".join(item["name"] for item in products.data["results"]))
    print("Homepage new arrival image returned:", bool(home.data["new_arrivals"] and home.data["new_arrivals"][0]["product_image"]))
    with transaction.atomic():
        response = client.post("/newsletter/", {"email": "api-check@offday.invalid", "consent": True}, format="json", **request_args)
        print("Newsletter status:", response.status_code)
        print("Newsletter delivery status:", response.data["detail"])
        transaction.set_rollback(True)
    print("Temporary newsletter row persists:", NewsletterSubscription.objects.filter(email="api-check@offday.invalid").exists())
