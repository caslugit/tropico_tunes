from sqlalchemy import or_
from flask import Blueprint, render_template, request

from app.models import Category, Color, Product, ProductVariant, Size


shop_bp = Blueprint("shop", __name__)


@shop_bp.get("/")
def home():
    featured = Product.query.filter_by(active=True, featured=True).limit(4).all()
    newest = Product.query.filter_by(active=True).order_by(Product.created_at.desc()).limit(4).all()
    return render_template("shop/home.html", featured=featured, newest=newest, categories=Category.query.all())


@shop_bp.get("/produtos")
def catalog():
    query = Product.query.filter_by(active=True)
    search = request.args.get("q", "").strip()
    category = request.args.get("categoria", "").strip()
    color = request.args.get("cor", "", type=str).strip()
    size = request.args.get("tamanho", "", type=str).strip()
    min_price = request.args.get("preco_min", type=float)
    max_price = request.args.get("preco_max", type=float)
    if search:
        query = query.filter(or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))
    if category:
        query = query.join(Category).filter(Category.slug == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if color or size:
        query = query.join(ProductVariant)
        if color:
            query = query.join(Color).filter(Color.name == color)
        if size:
            query = query.join(Size).filter(Size.name == size)
        query = query.filter(ProductVariant.stock > 0).distinct()
    order = request.args.get("ordem", "recentes")
    if order == "menor-preco":
        query = query.order_by(Product.price.asc())
    elif order == "maior-preco":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    return render_template("shop/catalog.html", products=query.all(), categories=Category.query.all(), colors=Color.query.order_by(Color.name).all(), sizes=Size.query.order_by(Size.sort_order).all(), search=search, selected_category=category, selected_color=color, selected_size=size, min_price=min_price, max_price=max_price, order=order)


@shop_bp.get("/produto/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, active=True).first_or_404()
    related = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.active.is_(True)).limit(4).all()
    return render_template("shop/product.html", product=product, related=related)

