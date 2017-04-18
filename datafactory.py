from models import Product, PriceHistory


def history():
    products = Product.query.all()
    
    history = {}
    
    for product in products:
        product_history = [ prod.value for prod in PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.timestep.asc())]
        history[product.name] = (product_history, product.colour)
    
    return history
        
        
def volumes():
    products = Product.query.all()
    
    volume = {}
    
    for product in products:
        product_volume = [ prod.in_circulation for prod in PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.timestep.asc())]
        volume[product.name] = (product_volume, product.colour, product.in_circulation)
    
    return volume
    
    
def totals():
    products = Product.query.all()
    
    totals = {}
    
    for product in products:
        product_total = [ prod.total_sold for prod in PriceHistory.query.filter_by(product_id=product.id).order_by(PriceHistory.timestep.asc())]
        totals[product.name] = (product_total, product.colour)
    
    return totals
    
