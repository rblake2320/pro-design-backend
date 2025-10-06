from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.product import Product, ProductVariant
from src.models.order import Order, OrderItem, CustomOrder
import json

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/create', methods=['POST'])
def create_order():
    """Create a new order (guest or authenticated)"""
    try:
        data = request.get_json()
        
        # Get user ID if authenticated
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        # Validate required fields
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        # Calculate totals
        subtotal = 0
        order_items = []
        
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
            
            quantity = item_data.get('quantity', 1)
            price = product.base_price
            subtotal += price * quantity
            
            order_items.append({
                'product_id': product.id,
                'variant_id': item_data.get('variant_id'),
                'quantity': quantity,
                'price_at_purchase': price,
                'custom_text': item_data.get('custom_text'),
                'custom_image_url': item_data.get('custom_image_url'),
                'custom_notes': item_data.get('custom_notes')
            })
        
        # Calculate tax and shipping
        tax = subtotal * 0.08  # 8% tax
        shipping = 10.00 if subtotal < 100 else 0.00  # Free shipping over $100
        total = subtotal + tax + shipping
        
        # Create order
        order = Order(
            user_id=user_id,
            customer_email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=total,
            shipping_address=json.dumps(data.get('shipping_address', {})),
            billing_address=json.dumps(data.get('billing_address', {}))
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get all orders for the current user"""
    try:
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if user is authorized to view this order
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id and order.user_id != user_id:
                user = User.query.get(user_id)
                if not user or not user.is_admin:
                    return jsonify({'error': 'Unauthorized'}), 403
        except:
            pass
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:order_id>/track', methods=['GET'])
def track_order(order_id):
    """Track order status"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'order_number': order.order_number,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/custom-quote', methods=['POST'])
def request_custom_quote():
    """Request a custom order quote"""
    try:
        data = request.get_json()
        
        # Get user ID if authenticated
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        # Create custom order request
        custom_order = CustomOrder(
            user_id=user_id,
            design_type=data.get('design_type'),
            design_data=json.dumps(data.get('design_data', {})),
            front_design=data.get('front_design'),
            back_design=data.get('back_design'),
            notes=data.get('notes'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone')
        )
        
        db.session.add(custom_order)
        db.session.commit()
        
        return jsonify({
            'message': 'Custom order request submitted successfully',
            'custom_order': custom_order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
