from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category


CATEGORIES = {
    "Clothes & Fashion": [
        "Men",
        "Women",
        "Kids",
        "Saree",
        "Kurta & Ethnic Wear",
        "Shirts & T-Shirts",
        "Jeans & Trousers",
        "Winter Wear",
    ],

    "Fruits & Vegetables": [
        "Fresh Fruits",
        "Vegetables",
        "Leafy Vegetables",
        "Seasonal Fruits",
        "Seasonal Vegetables",
    ],

    "Grocery / Kirana": [
        "Rice & Grains",
        "Dal & Pulses",
        "Atta & Flour",
        "Oil & Ghee",
        "Spices & Masala",
        "Sugar & Salt",
        "Tea & Coffee",
        "Biscuits & Snacks",
        "Dry Fruits",
        "Pickles & Papad",
    ],

    "Desi Mitti & Handicrafts": [
        "Matka",
        "Surahi",
        "Kulhad",
        "Diya",
        "Mitti ke Bartan",
        "Bamboo Products",
        "Wooden Products",
        "Handmade Items",
    ],

    "Dairy & Fresh Products": [
        "Milk",
        "Curd",
        "Paneer",
        "Butter",
        "Ghee",
        "Chhachh",
        "Eggs",
    ],

    "Kitchen & Utensils": [
        "Steel Utensils",
        "Aluminium Utensils",
        "Copper & Brass",
        "Plates & Bowls",
        "Glasses & Cups",
        "Cookware",
        "Kitchen Tools",
        "Storage Containers",
    ],

    "Home & Living": [
        "Bedsheets",
        "Pillows",
        "Curtains",
        "Mats & Carpets",
        "Cleaning Products",
        "Bathroom Items",
        "Home Decoration",
        "Buckets & Mugs",
    ],

    "Footwear": [
        "Men Footwear",
        "Women Footwear",
        "Kids Footwear",
        "Shoes",
        "Sandals",
        "Chappals & Slippers",
        "Jutti & Mojari",
    ],

    "Electronics & Mobile Accessories": [
        "Chargers & Cables",
        "Earphones & Headphones",
        "Speakers",
        "Mobile Accessories",
        "LED Bulbs",
        "Batteries",
        "Small Electronics",
    ],

    "Beauty & Personal Care": [
        "Soap",
        "Shampoo",
        "Hair Oil",
        "Skin Care",
        "Cosmetics",
        "Perfume",
        "Personal Hygiene",
    ],

    "Toys & Kids": [
        "Toys",
        "Educational Toys",
        "Traditional Toys",
        "Baby Products",
        "Kids Accessories",
    ],

    "Books & Stationery": [
        "Books",
        "Notebooks",
        "Pens & Pencils",
        "School Supplies",
        "Art & Craft",
        "Office Stationery",
        "School Bags",
    ],

    "Puja & Religious Items": [
        "Agarbatti & Dhoop",
        "Diya & Lamps",
        "Puja Samagri",
        "Puja Thali",
        "Kalash",
        "Religious Decorations",
    ],

    "Agriculture & Gardening": [
        "Seeds",
        "Plants",
        "Gardening Tools",
        "Farming Tools",
        "Pots & Planters",
        "Agriculture Supplies",
    ],

    "Hardware & Household Tools": [
        "Hand Tools",
        "Locks",
        "Nuts & Bolts",
        "Ropes",
        "Plumbing Items",
        "Electrical Items",
        "Repair Items",
    ],

    "Gifts & Festival": [
        "Gift Items",
        "Diwali",
        "Holi",
        "Rakhi",
        "Wedding Items",
        "Festival Decoration",
    ],

    "Local & Village Products": [
        "Homemade Products",
        "Village Food",
        "Traditional Products",
        "Local Crafts",
        "Regional Specialties",
    ],
}


class Command(BaseCommand):
    help = "Create Apna Market categories and subcategories"

    def handle(self, *args, **options):

        for category_name, subcategories in CATEGORIES.items():

            # Main category ka unique slug
            base_slug = slugify(category_name)

            parent = Category.objects.filter(
                name=category_name,
                parent__isnull=True
            ).first()

            if parent is None:

                slug = base_slug

                # Agar slug kisi existing category ka hai,
                # to unique slug generate karo.
                if Category.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-category"

                counter = 2

                while Category.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-category-{counter}"
                    counter += 1

                parent = Category.objects.create(
                    name=category_name,
                    slug=slug,
                    parent=None
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created category: {category_name}"
                    )
                )

            # Subcategories
            for subcategory_name in subcategories:

                existing = Category.objects.filter(
                    name=subcategory_name,
                    parent=parent
                ).first()

                if existing:
                    continue

                base_sub_slug = slugify(
                    f"{category_name}-{subcategory_name}"
                )

                slug = base_sub_slug
                counter = 2

                while Category.objects.filter(slug=slug).exists():
                    slug = f"{base_sub_slug}-{counter}"
                    counter += 1

                Category.objects.create(
                    name=subcategory_name,
                    slug=slug,
                    parent=parent
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Created subcategory: {subcategory_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Apna Market categories created successfully!"
            )
        )