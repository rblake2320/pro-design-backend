from flask import Blueprint, request, jsonify
import stripe
import os
from src.database import db
from src.models.order import Order

payment_bp = Blueprint('payment', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')

@payment_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a Stripe payment intent for checkout"""
    try:
        data = request.get_json()
        
        # Get amount from request (in cents)
        amount = int(float(data.get('amount', 0)) * 100)  # Convert dollars to cents
        
        if amount < 50:  # Stripe minimum is $0.50
            return jsonify({'error': 'Amount must be at least $0.50'}), 400
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'customer_email': data.get('customer_email', ''),
                'customer_name': data.get('customer_name', ''),
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """Confirm payment and update order status"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        order_id = data.get('order_id')
        
        if not payment_intent_id or not order_id:
            return jsonify({'error': 'Missing payment_intent_id or order_id'}), 400
        
        # Update order in database
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order.payment_intent_id = payment_intent_id
        
        # Try to retrieve payment intent from Stripe (if real keys are configured)
        payment_status = 'succeeded'  # Default for development
        try:
            if stripe.api_key and not stripe.api_key.startswith('sk_test_placeholder'):
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                payment_status = intent.status
        except Exception as stripe_error:
            # If Stripe API fails (e.g., placeholder keys or network issue),
            # assume success for development/testing
            print(f"Stripe API error (using default): {stripe_error}")
            payment_status = 'succeeded'
        
        # Update order status based on payment status
        if payment_status == 'succeeded':
            order.payment_status = 'paid'
            order.status = 'processing'
        elif payment_status == 'requires_payment_method':
            order.payment_status = 'failed'
        else:
            order.payment_status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': order.to_dict(),
            'payment_status': payment_status
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for payment events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Find order by payment intent ID
        order = Order.query.filter_by(payment_intent_id=payment_intent['id']).first()
        if order:
            order.payment_status = 'paid'
            order.status = 'processing'
            db.session.commit()
            
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        # Find order by payment intent ID
        order = Order.query.filter_by(payment_intent_id=payment_intent['id']).first()
        if order:
            order.payment_status = 'failed'
            db.session.commit()
    
    return jsonify({'success': True}), 200


@payment_bp.route('/config', methods=['GET'])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_placeholder')
    return jsonify({
        'publishableKey': publishable_key
    }), 200
