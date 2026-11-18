from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import click

from .extensions import db
from .models import Address, Category, Color, Coupon, Product, ProductImage, ProductVariant, Size, User


PRODUCTS = [
    ("Camiseta Essencial TROPICO", "camiseta-sol-nascente", "Camisetas", "Camiseta oversized em algodão encorpado, disponível em preto e off-white.", "159.90", True, "/static/images/products/camiseta-sol-nascente.jpeg"),
    ("Moletom Preto TROPICO", "moletom-horizonte", "Moletons", "Moletom preto felpado com capuz, bolso canguru e logo TROPICO.", "329.90", True, "/static/images/products/moletom-horizonte.png"),
    ("Calça Cargo Preta", "calca-cargo-cerrado", "Calças", "Calça cargo preta de modelagem ampla, com bolsos utilitários.", "289.90", True, "/static/images/products/calca-cargo-cerrado.jpeg"),
    ("Short Street", "short-orla", "Shorts", "Short leve e funcional para o dia a dia.", "189.90", False, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=900&q=80"),
    ("Corta-Vento Preto TROPICO", "jaqueta-chuva-verao", "Jaquetas", "Corta-vento preto com capuz, acabamento repelente e logo TROPICO.", "399.90", True, "/static/images/products/jaqueta-chuva-verao.jpeg"),
    ("Regata Branca TROPICO", "regata-mare", "Camisetas", "Regata branca em algodão, com logo TROPICO aplicado no peito.", "109.90", False, "/static/images/products/regata-mare.jpeg"),
    ("Ecobag TROPICO", "ecobag-raizes", "Acessórios", "Ecobag em lona de algodão cru, com estampa frontal TROPICO.", "79.90", False, "/static/images/products/ecobag-raizes.jpeg"),
    ("Camiseta Essencial Areia", "camiseta-essencial-areia", "Camisetas", "Camiseta oversized em algodão encorpado off-white, com assinatura TRÓPICO no peito.", "179.90", True, "/static/images/products/camiseta-essencial-areia.png"),
    ("Jeans Noite TRÓPICO", "jeans-noite", "Calças", "Jeans preto estonado de modelagem ampla, construção robusta e etiqueta exclusiva TRÓPICO.", "349.90", True, "/static/images/products/jeans-noite.png"),
    ("Corta-Vento Mata TRÓPICO", "corta-vento-mata", "Jaquetas", "Corta-vento verde-mata em tecido técnico leve, com capuz, meio zíper e bolso canguru.", "419.90", True, "/static/images/products/corta-vento-mata.png"),
    ("Gorro Terra TRÓPICO", "gorro-terra", "Acessórios", "Gorro canelado terracota em malha macia, com etiqueta tecida TRÓPICO.", "129.90", False, "/static/images/products/gorro-terra.png"),
]


PRODUCT_VARIANTS = {
    "camiseta-sol-nascente": (["P", "M", "G", "GG"], ["Preto", "Off-white"]),
    "regata-mare": (["P", "M", "G", "GG"], ["Off-white"]),
    "ecobag-raizes": (["Único"], ["Off-white"]),
    "camiseta-essencial-areia": (["P", "M", "G", "GG"], ["Off-white"]),
    "jeans-noite": (["P", "M", "G", "GG"], ["Preto"]),
    "corta-vento-mata": (["P", "M", "G", "GG"], ["Verde Mata"]),
    "gorro-terra": (["Único"], ["Terracota"]),
}


def variant_names(slug):
    return PRODUCT_VARIANTS.get(slug, (["P", "M", "G", "GG"], ["Preto"]))


def sync_catalog():
    """Atualiza os produtos do catálogo sem apagar dados operacionais."""
    categories = {}
    for name in sorted({row[2] for row in PRODUCTS}):
        category = Category.query.filter_by(name=name).first()
        if category is None:
            category = Category(name=name, slug=name.lower().replace("ó", "o").replace("é", "e").replace(" ", "-"))
            db.session.add(category)
            db.session.flush()
        categories[name] = category

    sizes = {}
    for index, name in enumerate(["P", "M", "G", "GG", "Único"]):
        size = Size.query.filter_by(name=name).first()
        if size is None:
            size = Size(name=name, sort_order=index if name != "Único" else 99)
            db.session.add(size)
            db.session.flush()
        sizes[name] = size

    colors = {}
    for name, hex_code in [("Preto", "#171717"), ("Off-white", "#EDE9DF"), ("Verde Mata", "#244A35"), ("Terracota", "#B94F2C")]:
        color = Color.query.filter_by(name=name).first()
        if color is None:
            color = Color(name=name, hex_code=hex_code)
            db.session.add(color)
            db.session.flush()
        colors[name] = color

    updated = 0
    for name, slug, category_name, description, price, featured, image in PRODUCTS:
        product = Product.query.filter_by(slug=slug).first()
        if product is None:
            product = Product(slug=slug)
            db.session.add(product)
        product.name = name
        product.category_id = categories[category_name].id
        product.description = description
        product.price = Decimal(price)
        product.featured = featured
        product.active = True
        if product.images:
            product.images[0].url = image
            product.images[0].alt_text = name
        else:
            product.images.append(ProductImage(url=image, alt_text=name))
        db.session.flush()
        size_names, color_names = variant_names(slug)
        existing = {(variant.size.name, variant.color.name) for variant in product.variants}
        for size_name in size_names:
            for color_name in color_names:
                if (size_name, color_name) not in existing:
                    product.variants.append(ProductVariant(size_id=sizes[size_name].id, color_id=colors[color_name].id, sku=f"TRP-{slug[:12].upper()}-{sizes[size_name].id}-{colors[color_name].id}", stock=8))
        updated += 1
    for retired_slug in {"camiseta-mata-atlantica", "bone-brisa", "camisa-amazonia"}:
        retired = Product.query.filter_by(slug=retired_slug).first()
        if retired:
            retired.active = False
    return updated


def register_commands(app):
    @app.cli.command("sync-catalog")
    def sync_catalog_command():
        db.create_all()
        updated = sync_catalog()
        db.session.commit()
        click.echo(f"Catálogo sincronizado: {updated} produtos atualizados.")

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Recria todas as tabelas.")
    def seed(reset):
        if reset:
            db.drop_all()
        db.create_all()
        if User.query.first():
            updated = sync_catalog()
            db.session.commit()
            click.echo(f"Banco existente preservado; {updated} produtos atualizados.")
            return
        admin = User(name="Admin TRÓPICO", email="admin@tropico.com.br", role="admin", phone="11999990000")
        admin.set_password("Admin@123")
        customer = User(name="Cliente Demo", email="cliente@tropico.com.br", phone="11988887777")
        customer.set_password("Cliente@123")
        db.session.add_all([admin, customer])
        db.session.flush()
        db.session.add(Address(user_id=customer.id, street="Rua das Palmeiras", number="100", neighborhood="Jardins", city="São Paulo", state="SP", zip_code="01400-000"))
        categories = {}
        for name in sorted({row[2] for row in PRODUCTS}):
            category = Category(name=name, slug=name.lower().replace("ó", "o").replace("é", "e").replace(" ", "-"))
            db.session.add(category)
            categories[name] = category
        size_list = [Size(name=name, sort_order=i if name != "Único" else 99) for i, name in enumerate(["P", "M", "G", "GG", "Único"])]
        color_list = [Color(name="Preto", hex_code="#171717"), Color(name="Off-white", hex_code="#EDE9DF"), Color(name="Verde Mata", hex_code="#244A35"), Color(name="Terracota", hex_code="#B94F2C")]
        db.session.add_all(size_list + color_list)
        db.session.flush()
        sizes = {size.name: size for size in size_list}
        colors = {color.name: color for color in color_list}
        for index, (name, slug, category_name, description, price, featured, image) in enumerate(PRODUCTS):
            product = Product(name=name, slug=slug, category_id=categories[category_name].id, description=description, price=Decimal(price), featured=featured)
            product.images.append(ProductImage(url=image, alt_text=name))
            db.session.add(product)
            db.session.flush()
            size_names, color_names = variant_names(slug)
            for size_name in size_names:
                for color_name in color_names:
                    size = sizes[size_name]
                    color = colors[color_name]
                    product.variants.append(ProductVariant(size_id=size.id, color_id=color.id, sku=f"TRP-{index+1:02d}-{size.name}-{color.id}", stock=3 + ((index + size.id + color.id) % 12)))
        db.session.add(Coupon(code="BEMVINDO10", discount_type="percent", value=10, active=True, max_uses=500, valid_until=datetime.now(timezone.utc) + timedelta(days=365)))
        db.session.commit()
        click.echo("Dados criados. Admin: admin@tropico.com.br / Admin@123")
