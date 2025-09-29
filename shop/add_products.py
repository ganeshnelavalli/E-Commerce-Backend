import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from website.models import Products

# Sample products to add
products = [
    {
        'name': 'iPhone 14 Pro',
        'description': 'Latest Apple iPhone with A16 Bionic chip and amazing camera system',
        'price': 999.99
    },
    {
        'name': 'Samsung Galaxy S23 Ultra',
        'description': 'Flagship Android phone with S-Pen and 200MP camera',
        'price': 1199.99
    },
    {
        'name': 'MacBook Pro 16"',
        'description': 'Powerful laptop with M2 Pro chip and stunning Retina display',
        'price': 2499.99
    },
    {
        'name': 'AirPods Pro',
        'description': 'Wireless earbuds with active noise cancellation and spatial audio',
        'price': 249.99
    },
    {
        'name': 'iPad Air',
        'description': 'Versatile tablet with M1 chip and 10.9-inch Liquid Retina display',
        'price': 599.99
    },
    {
        'name': 'Sony WH-1000XM4',
        'description': 'Premium wireless headphones with industry-leading noise cancellation',
        'price': 349.99
    },
    {
        'name': 'Nintendo Switch OLED',
        'description': 'Gaming console with vibrant 7-inch OLED screen',
        'price': 349.99
    },
    {
        'name': 'Dell XPS 15',
        'description': 'Premium Windows laptop with 4K display and RTX graphics',
        'price': 1999.99
    }
]

def add_products():
    for product in products:
        try:
            # Check if product already exists
            if not Products.objects.filter(name=product['name']).exists():
                Products.objects.create(
                    name=product['name'],
                    description=product['description'],
                    price=product['price']
                )
                print(f"Added: {product['name']}")
            else:
                print(f"Skipped (already exists): {product['name']}")
        except Exception as e:
            print(f"Error adding {product['name']}: {str(e)}")

if __name__ == '__main__':
    print("Adding products to database...")
    add_products()
    print("Done!")