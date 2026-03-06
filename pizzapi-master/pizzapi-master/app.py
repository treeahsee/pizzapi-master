import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session
from pizzapy import Customer, StoreLocator, Order, CreditCard
from pizzapy.menu import Menu
from pizzapy.urls import Urls
from pizzapy.utils import request_json

app = Flask(__name__)
app.secret_key = 'dominos-pizza-ui-secret'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/find-store', methods=['POST'])
def find_store():
    data = request.json
    try:
        customer = Customer(
            fname=data['first_name'],
            lname=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
        )
        store = StoreLocator.find_closest_store_to_customer(customer)

        session['customer'] = {
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone,
            'address': data['address'],
        }
        session['store_id'] = store.id
        session['cart'] = []

        return jsonify({
            'success': True,
            'store': {
                'id': store.id,
                'address': store.data.get('AddressDescription', 'Unknown'),
                'is_open': store.data.get('IsOpen', False),
                'phone': store.data.get('Phone', ''),
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/search-menu', methods=['POST'])
def search_menu():
    data = request.json
    query = data.get('query', '').strip().lower()

    if 'store_id' not in session:
        return jsonify({'success': False, 'error': 'No store selected'}), 400

    try:
        urls = Urls('us')
        response = request_json(urls.menu_url(), store_id=session['store_id'], lang='en')
        menu = Menu(response)

        results = []
        for code, variant in menu.variants.items():
            name = variant.get('Name', '')
            if not query or query in name.lower():
                price = variant.get('Price', '0')
                try:
                    price_float = float(price)
                except (ValueError, TypeError):
                    price_float = 0.0
                if price_float > 0:
                    results.append({
                        'code': variant['Code'],
                        'name': name,
                        'price': price,
                        'size': variant.get('SizeCode', ''),
                    })

        results.sort(key=lambda x: x['name'])
        return jsonify({'success': True, 'items': results[:60]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cart/add', methods=['POST'])
def cart_add():
    data = request.json
    cart = session.get('cart', [])
    cart.append({'code': data['code'], 'name': data['name'], 'price': data['price']})
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart, 'total': _cart_total(cart)})


@app.route('/api/cart/remove', methods=['POST'])
def cart_remove():
    idx = request.json.get('index')
    cart = session.get('cart', [])
    if 0 <= idx < len(cart):
        cart.pop(idx)
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart, 'total': _cart_total(cart)})


@app.route('/api/cart', methods=['GET'])
def cart_get():
    cart = session.get('cart', [])
    return jsonify({'success': True, 'cart': cart, 'total': _cart_total(cart)})


@app.route('/api/validate-order', methods=['POST'])
def validate_order():
    data = request.json

    if 'customer' not in session or 'store_id' not in session:
        return jsonify({'success': False, 'error': 'Missing customer or store info'}), 400
    if not session.get('cart'):
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400

    try:
        cust = session['customer']
        customer = Customer(
            fname=cust['first_name'], lname=cust['last_name'],
            email=cust['email'], phone=cust['phone'], address=cust['address'],
        )
        store = StoreLocator.find_closest_store_to_customer(customer)
        order = Order.begin_customer_order(customer, store)

        failed_items = []
        for item in session['cart']:
            try:
                order.add_item(item['code'])
            except Exception:
                failed_items.append(item['code'])

        card_data = data.get('card')
        if card_data:
            card = CreditCard(
                number=card_data['number'].replace(' ', ''),
                card_expiry=card_data['expiry'].replace('/', ''),
                cvv=card_data['cvv'],
                zip=card_data['zip'],
            )
        else:
            card = False

        response = order.pay_with(card)
        status = response.get('Status', 0)
        amounts = response.get('Order', {}).get('Amounts', {})
        customer_total = amounts.get('Customer', response.get('Order', {}).get('Amounts', {}).get('Payment', '?'))

        return jsonify({
            'success': True,
            'status': status,
            'total': customer_total,
            'failed_items': failed_items,
            'message': 'Order validated! (not actually placed)' if status != -1 else 'Validation failed',
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def _cart_total(cart):
    total = 0.0
    for item in cart:
        try:
            total += float(item['price'])
        except (ValueError, TypeError):
            pass
    return round(total, 2)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
