from flask import Blueprint, request, jsonify
from src.database import db
from src.models.product import Product, ProductVariant

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Product.query.filter_by(is_active=True)
        
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        
        products = query.all()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<int:product_id>/variants', methods=['GET'])
def get_product_variants(product_id):
    """Get all variants for a product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        variants = ProductVariant.query.filter_by(product_id=product_id).all()
        
        return jsonify({
            'variants': [v.to_dict() for v in variants]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        
        return jsonify({
            'categories': [cat[0] for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
