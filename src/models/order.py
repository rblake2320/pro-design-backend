from datetime import datetime
import secrets
from src.database import db
from src.models.product import Product, ProductVariant

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for guest checkout
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered, cancelled
    
    # Customer info (for guest checkout)
    customer_email = db.Column(db.String(200))
    customer_name = db.Column(db.String(200))
    customer_phone = db.Column(db.String(50))
    
    # Pricing
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, default=0.0)
    shipping = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)
    
    # Payment
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed, refunded
    payment_intent_id = db.Column(db.String(200))  # Stripe payment intent ID
    
    # Addresses (stored as JSON strings)
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        """Generate a unique order number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = secrets.token_hex(4).upper()
        return f'PDC-{timestamp}-{random_part}'
    
    def to_dict(self):
        import json
        
        # Parse JSON strings for addresses
        shipping_addr = None
        billing_addr = None
        
        try:
            if self.shipping_address:
                shipping_addr = json.loads(self.shipping_address) if isinstance(self.shipping_address, str) else self.shipping_address
        except:
            shipping_addr = None
            
        try:
            if self.billing_address:
                billing_addr = json.loads(self.billing_address) if isinstance(self.billing_address, str) else self.billing_address
        except:
            billing_addr = None
        
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'status': self.status,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'shipping': self.shipping,
            'total': self.total,
            'payment_status': self.payment_status,
            'payment_method': 'manual',  # Default payment method
            'shipping_address': shipping_addr,
            'billing_address': billing_addr,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)
    
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    
    # Custom order fields
    custom_text = db.Column(db.Text)
    custom_image_url = db.Column(db.String(500))
    custom_notes = db.Column(db.Text)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')
    variant = db.relationship('ProductVariant', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'variant_id': self.variant_id,
            'variant_size': self.variant.size if self.variant else None,
            'size': self.variant.size if self.variant else None,  # Add size field for frontend
            'quantity': self.quantity,
            'price': self.price_at_purchase,  # Add price field for frontend compatibility
            'price_at_purchase': self.price_at_purchase,
            'custom_text': self.custom_text,
            'custom_image_url': self.custom_image_url,
            'custom_notes': self.custom_notes,
            'custom_design': bool(self.custom_text or self.custom_image_url)  # Flag for custom designs
        }


class CustomOrder(db.Model):
    __tablename__ = 'custom_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Design details
    design_type = db.Column(db.String(50))  # text, image, logo
    design_data = db.Column(db.Text)  # JSON string
    front_design = db.Column(db.String(500))
    back_design = db.Column(db.String(500))
    notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(50), default='pending_approval')  # pending_approval, approved, in_production, completed
    admin_notes = db.Column(db.Text)
    
    # Contact info
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'design_type': self.design_type,
            'design_data': self.design_data,
            'front_design': self.front_design,
            'back_design': self.back_design,
            'notes': self.notes,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
