from flask import Blueprint, render_template, request, redirect, url_for, abort
from mechanics import do_timestep
from datafactory import history, volumes, totals
from models import User, Product

# Used for non-crypto purpose
import random



router = Blueprint('', '')


@router.route('/')
def index():
    return render_template('index.html', history=history(), volumes=volumes(), totals=totals())
    
    
@router.route('/admin/<string:key>')
def admin(key):
    if (key != "SOMEKEY"):
        abort(403)
    return render_template('admin.html', users=User.query.all(), products=Product.query.all())
    
    
@router.route('/step')
def dostep():
    do_timestep()
    return ''
