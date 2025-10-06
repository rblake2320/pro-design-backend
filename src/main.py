import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.database import db
from src.models.user import User
from src.models.product import Product, ProductVariant
from src.models.order import Order, OrderItem, CustomOrder

# Import routes
from src.routes.user import user_bp
from src.routes.products import products_bp
from src.routes.orders import orders_bp
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'pro-design-company-secret-key-2025'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-pro-design-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

def seed_products():
    """Seed initial products"""
    from src.models.user import User
    
    products_data = [
        {
            'name': 'Classic Black Tee',
            'description': 'Premium quality 100% cotton t-shirt. Perfect for custom designs and everyday wear.',
            'category': 'tshirt',
            'base_price': 25.00,
            'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL', '3XL']
        },
        {
            'name': 'Custom Design Hoodie',
            'description': 'Comfortable fleece hoodie with front pocket. Ideal for screen printing and embroidery.',
            'category': 'hoodie',
            'base_price': 45.00,
            'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL']
        },
        {
            'name': 'Graphic Print Tee',
            'description': 'Soft cotton blend t-shirt perfect for vibrant custom graphics and designs.',
            'category': 'tshirt',
            'base_price': 28.00,
            'image_url': 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL']
        },
        {
            'name': 'Premium Cotton Tee',
            'description': 'High-quality ring-spun cotton t-shirt. Excellent for detailed custom printing.',
            'category': 'tshirt',
            'base_price': 30.00,
            'image_url': 'https://images.unsplash.com/photo-1622445275463-afa2ab738c34?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL']
        },
        {
            'name': 'Pullover Hoodie',
            'description': 'Heavyweight pullover hoodie with adjustable drawstring. Perfect for custom logos.',
            'category': 'hoodie',
            'base_price': 50.00,
            'image_url': 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL']
        },
        {
            'name': 'Vintage Style Tee',
            'description': 'Retro-inspired t-shirt with a worn-in feel. Great for vintage designs.',
            'category': 'tshirt',
            'base_price': 26.00,
            'image_url': 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL']
        },
        {
            'name': 'Zip-Up Hoodie',
            'description': 'Full-zip hoodie with side pockets. Excellent for custom embroidery and printing.',
            'category': 'hoodie',
            'base_price': 55.00,
            'image_url': 'https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?w=500&h=600&fit=crop',
            'sizes': ['M', 'L', 'XL', '2XL']
        },
        {
            'name': 'Performance Tee',
            'description': 'Moisture-wicking athletic t-shirt. Perfect for sports teams and active wear.',
            'category': 'tshirt',
            'base_price': 32.00,
            'image_url': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL', '3XL']
        },
        {
            'name': 'Long Sleeve Tee',
            'description': 'Comfortable long sleeve t-shirt. Great for cooler weather custom designs.',
            'category': 'tshirt',
            'base_price': 35.00,
            'image_url': 'https://images.unsplash.com/photo-1618517351616-38fb9c5210c6?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL']
        },
        {
            'name': 'Crewneck Sweatshirt',
            'description': 'Classic crewneck sweatshirt with ribbed cuffs. Perfect for custom screen printing.',
            'category': 'hoodie',
            'base_price': 42.00,
            'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&h=600&fit=crop',
            'sizes': ['S', 'M', 'L', 'XL', '2XL', '3XL']
        }
    ]
    
    for prod_data in products_data:
        sizes = prod_data.pop('sizes')
        product = Product(**prod_data)
        db.session.add(product)
        db.session.flush()  # Get product ID
        
        # Add variants for each size
        for size in sizes:
            variant = ProductVariant(
                product_id=product.id,
                size=size,
                color='Black',
                stock_quantity=100,
                sku=f"{product.name.replace(' ', '-').upper()}-{size}-BLK"
            )
            db.session.add(variant)
    
    db.session.commit()
    print("✅ Seeded products successfully!")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Initialize database and seed data
    with app.app_context():
        db.create_all()
        
        # Seed initial data if database is empty
        if Product.query.count() == 0:
            seed_products()
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(email='admin@prodesign.com').first()
        if not admin:
            admin = User(
                email='admin@prodesign.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@prodesign.com / admin123")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
