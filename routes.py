from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask import current_app as app
from mechanics import do_timestep
from datafactory import history, volumes, totals
from models import User, Product, PriceHistory, db

# Used for non-crypto purpose
import random

router = Blueprint('', '')

@router.route('/')
def index():
    return render_template('index.html', history=history(), volumes=volumes(), totals=totals())
    
    
@router.route('/admin/<string:key>')
def admin(key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    return render_template('admin.html', users=User.query.all(), products=Product.query.all(), key=key)
    
    
@router.route('/step')
def dostep():
    do_timestep()
    return ''
    
    
@router.route('/sim')
def dosim():
    for product in Product.query.all():
        product.current_value = 50 # int(100 * random.random())
        product.global_trend = 0
        product.next_timestep = 0
        product.crash_potential = 0.2 * random.random()
        product.total_sold = 0
        product.in_circulation = 0
    PriceHistory.query.delete()
    db.session.commit()
    for i in range(60):
        do_timestep()
    return ''
    
    
@router.route('/sell/<int:userid>/<int:prdid>/<string:key>')
def sell(userid, prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    user = User.query.get_or_404(userid)
    prd = Product.query.get_or_404(prdid)
    
    user.points -= prd.current_value
    prd.sell_amount += 1
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
    
@router.route('/buy/<int:userid>/<int:prdid>/<string:key>')
def buy(userid, prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    user = User.query.get_or_404(userid)
    prd = Product.query.get_or_404(prdid)
    
    user.points += prd.current_value
    prd.buy_amount += 1
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
    
@router.route('/manipulate/sell/up/<int:prdid>/<string:key>')
def sellup(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.sell_amount += 5
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
@router.route('/manipulate/sell/down/<int:prdid>/<string:key>')
def selldown(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.sell_amount -= 5
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
@router.route('/manipulate/buy/up/<int:prdid>/<string:key>')
def buyup(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.buy_amount += 5
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
@router.route('/manipulate/buy/down/<int:prdid>/<string:key>')
def buydown(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.buy_amount -= 5
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
    
@router.route('/manipulate/value/<int:prdid>/<int:amount>/<string:key>')
def valmanip(prdid, amount, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.global_trend += amount-5
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
    
@router.route('/manipulate/crash/up/<int:prdid>/<string:key>')
def crashup(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.crash_potential += 0.005
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
    
@router.route('/manipulate/crash/garantueed/<int:prdid>/<string:key>')
def crashgarantueed(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.crash_potential = 1.0
    db.session.commit()
    return redirect(url_for(".admin", key=key))
    
@router.route('/manipulate/crash/down/<int:prdid>/<string:key>')
def crashdown(prdid, key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    prd = Product.query.get_or_404(prdid)
    prd.sell_amount -= 0.005
    db.session.commit()
    return redirect(url_for(".admin", key=key))


@router.route('/adduser/<string:key>', methods=["POST"])
def adduser( key):
    if (key != app.config.get("Adminkey")):
        abort(403)
    user = User(username=request.form.get("username"), points=200)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for(".admin", key=key))
