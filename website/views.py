# create standard routes


from distutils.command.config import config
from flask import Blueprint, render_template, flash, request, request_started, session, url_for, redirect
from flask_login import login_required, current_user
import stripe
# added import for 'Items' table
from .models import Items, Cart
from . import db


views = Blueprint('views', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@views.route('/', methods=['GET', 'POST'])
def home():
  rows = Cart.query.filter(Cart.id).count()
  return render_template("home.html", user=current_user, rows=rows)

@views.route('/menu', methods=['GET', 'POST'])
def menu():
    rows = Cart.query.filter(Cart.id).count()
    return render_template('menu.html', user=current_user, items=get_items(), rows=rows)

@views.route('/item/<int:id>', methods=['GET', 'POST'])
def item(id):
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    cart_item = Cart(name=name, price=price)
    db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart!', category='success')
    return redirect(url_for('views.cart'))
  else:
    rows = Cart.query.filter(Cart.id).count()
    return render_template('item.html', user=current_user, current_item=get_items()[id - 1], rows = rows)

@views.route('/delete/<int:id>')
def delete(id):
  item_to_delete = Cart.query.get_or_404(id)
  try:
    db.session.delete(item_to_delete)
    db.session.commit()
    flash('Item removed from cart')
    return redirect(url_for('views.cart'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('views.cart'))

@views.route('/cart', methods=['GET', 'POST'])
def cart():
  rows = Cart.query.filter(Cart.id).count()
  return render_template('cart.html', user=current_user, item=get_cart_items(), rows=rows)

@views.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'Pizza',
        },
        'unit_amount': 1999,
      },
      'quantity': 1,
    }],
    mode='payment',
    success_url='http://127.0.0.1:5000/successful',
    cancel_url='http://127.0.0.1:5000/cart',
  )
    return redirect(session.url, code=303)

@views.route('/successful', methods=['GET', 'POST'])
def successful():
  rows = Cart.query.filter(Cart.id).count()
  return render_template('successful.html', user=current_user, rows=rows)

def get_items():
  ids = [id[0] for id in Items.query.with_entities(Items.id).all()] # fixed
  test_items = []
  for id in ids:
    item = Items.query.filter_by(id=id).first()
    grabber = {'id': 0, 'name': '', 'price': 0, 'desc': '', 'img': '', 'toppings': ['']}
    grabber['id'] = id
    grabber['name'] = item.name
    grabber['price'] = item.price
    grabber['desc'] = item.description
    grabber['img'] = item.item_image
    test_items.append(grabber)
  return test_items

def get_cart_items():
  ids = [id[0] for id in Cart.query.with_entities(Cart.id).all()]
  test_cart_items = []
  for id in ids:
    cart = Cart.query.filter_by(id=id).first()
    grabber = {'id': 0, 'name': '', 'price': 0}
    grabber['id'] = id
    grabber['name'] = cart.name
    grabber['price'] = cart.price
    test_cart_items.append(grabber)
  return test_cart_items
