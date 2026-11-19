import os
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
import django
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from myapp.models import Brand, Category, Product, ProductHighlight, ProductImage, ProductVariant, SubCategory

if settings.DATABASES["default"]["NAME"] != "new_store_db" or settings.DATABASES["default"].get("HOST") not in ("127.0.0.1", "localhost"):
    raise RuntimeError("Refusing to seed anything outside the local new_store_db")
if Product.objects.exists() or Category.objects.exists():
    raise RuntimeError("The local catalog is no longer empty; no records were changed")

asset_root = Path(r"D:\Offday-frontend\public\offday")
image_bytes = {
    "graphic_front": ("graphic-tee-front.jpeg", (asset_root / "graphic-tee-front.jpeg").read_bytes()),
    "oversized": ("oversized-tee.jpeg", (asset_root / "oversized-tee.jpeg").read_bytes()),
    "graphic_street": ("graphic-tee-street.jpeg", (asset_root / "graphic-tee-street.jpeg").read_bytes()),
}

with transaction.atomic():
    brand, _ = Brand.objects.get_or_create(name="OFFDAY COLLECTIONS")
    collection_specs = [
        ("OFFDAY DROPS", "Boxy fit", "graphic_front"),
        ("OFFDAY BASICS", "Relaxed fit", "oversized"),
        ("OFFDAY ESSENTIALS", "Relaxed fit", "graphic_street"),
        ("OFFDAY WINTER COLLECTIONS", "Layering", "oversized"),
    ]
    collections = {}
    for name, subcategory_name, photo_key in collection_specs:
        category = Category(name=name, is_active=True)
        filename, content = image_bytes[photo_key]
        category.image.save(f"{name.lower().replace(' ', '-')}.jpeg", ContentFile(content), save=True)
        subcategory = SubCategory.objects.create(category=category, name=subcategory_name, is_active=True)
        collections[name] = (category, subcategory)

    product_specs = [
        ("Drop Graphic Tee", "Washed black · Boxy fit", "OFFDAY DROPS", "Boxy fit", Decimal("129.00"), "Limited", "graphic_front"),
        ("The Heavyweight Tee", "Charcoal · Relaxed fit", "OFFDAY BASICS", "Relaxed fit", Decimal("119.00"), "", "oversized"),
        ("Everyday Graphic Tee", "Washed black · Relaxed fit", "OFFDAY ESSENTIALS", "Relaxed fit", Decimal("129.00"), "New drop", "graphic_street"),
    ]
    for name, description, category_name, subcategory_name, price, badge, photo_key in product_specs:
        category, subcategory = collections[category_name]
        product = Product.objects.create(
            category=category,
            subcategory=subcategory,
            brand=brand,
            name=name,
            description=description,
            key_features=badge,
            is_active=True,
        )
        variant = ProductVariant.objects.create(product=product, price_type="single", price=price, stock=0)
        filename, content = image_bytes[photo_key]
        product_image = ProductImage(variant=variant, is_primary=True, position=0)
        product_image.image.save(f"sample-{product.id}-{filename}", ContentFile(content), save=True)
        if badge:
            ProductHighlight.objects.create(
                product=product,
                text=badge,
                icon_key="tag",
                background_color="#C6F135",
                text_color="#111111",
                display_order=0,
                is_active=True,
            )

print("Categories:", Category.objects.count())
print("Products:", Product.objects.count())
print("Product images:", ProductImage.objects.count())
print("Seeded names:", ", ".join(Product.objects.order_by("id").values_list("name", flat=True)))
