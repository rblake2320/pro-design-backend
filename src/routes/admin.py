from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.product import Product, ProductVariant
from src.models.order import Order, OrderItem, CustomOrder
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to require admin access"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get admin dashboard statistics"""
    try:
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total)).filter_by(payment_status='paid').scalar() or 0
        total_customers = User.query.filter_by(is_admin=False).count()
        total_products = Product.query.filter_by(is_active=True).count()
        pending_orders = Order.query.filter_by(status='pending').count()
        pending_custom_orders = CustomOrder.query.filter_by(status='pending_approval').count()
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify({
            'stats': {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'total_customers': total_customers,
                'total_products': total_products,
                'pending_orders': pending_orders,
                'pending_custom_orders': pending_custom_orders
            },
            'recent_orders': [order.to_dict() for order in recent_orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders with filtering"""
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if 'status' in data:
            order.status = data['status']
        
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products', methods=['GET', 'POST'])
@admin_required
def manage_products():
    """Get all products or create new product"""
    if request.method == 'GET':
        try:
            products = Product.query.all()
            return jsonify({
                'products': [p.to_dict() for p in products]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            product = Product(
                name=data['name'],
                description=data.get('description'),
                category=data['category'],
                base_price=data['base_price'],
                image_url=data.get('image_url'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(product)
            db.session.flush()
            
            # Add variants if provided
            if 'variants' in data:
                for variant_data in data['variants']:
                    variant = ProductVariant(
                        product_id=product.id,
                        size=variant_data['size'],
                        color=variant_data.get('color', 'Black'),
                        stock_quantity=variant_data.get('stock_quantity', 100),
                        sku=variant_data.get('sku')
                    )
                    db.session.add(variant)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Product created successfully',
                'product': product.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<int:product_id>', methods=['PUT', 'DELETE'])
@admin_required
def update_delete_product(product_id):
    """Update or delete a product"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            if 'name' in data:
                product.name = data['name']
            if 'description' in data:
                product.description = data['description']
            if 'category' in data:
                product.category = data['category']
            if 'base_price' in data:
                product.base_price = data['base_price']
            if 'image_url' in data:
                product.image_url = data['image_url']
            if 'is_active' in data:
                product.is_active = data['is_active']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Product updated successfully',
                'product': product.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({'message': 'Product deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@admin_bp.route('/custom-orders', methods=['GET'])
@admin_required
def get_custom_orders():
    """Get all custom order requests"""
    try:
        status = request.args.get('status')
        
        query = CustomOrder.query
        
        if status:
            query = query.filter_by(status=status)
        
        custom_orders = query.order_by(CustomOrder.created_at.desc()).all()
        
        return jsonify({
            'custom_orders': [co.to_dict() for co in custom_orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/custom-orders/<int:custom_order_id>', methods=['PUT'])
@admin_required
def update_custom_order(custom_order_id):
    """Update custom order status"""
    try:
        data = request.get_json()
        custom_order = CustomOrder.query.get(custom_order_id)
        
        if not custom_order:
            return jsonify({'error': 'Custom order not found'}), 404
        
        if 'status' in data:
            custom_order.status = data['status']
        
        if 'admin_notes' in data:
            custom_order.admin_notes = data['admin_notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Custom order updated successfully',
            'custom_order': custom_order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/customers', methods=['GET'])
@admin_required
def get_customers():
    """Get all customers"""
    try:
        customers = User.query.filter_by(is_admin=False).all()
        
        return jsonify({
            'customers': [user.to_dict() for user in customers]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
