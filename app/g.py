# Create deployment-ready Flask + PyMongo app scaffold for "geniusbabycosmetics" and zip it for download
import os, json, textwrap, zipfile, pathlib, datetime, random, string

base_dir = "/home/harold/Desktop/geniusbabycosmetics"
paths = [
    "templates",
    "static/css",
    "static/js",
    "static/img",
    "sample_data",
]

# Helper to write files
def write(path, content):
    full = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

# Ensure directories
for p in paths:
    os.makedirs(os.path.join(base_dir, p), exist_ok=True)


# ---------------- templates/base.html ----------------
base_html = r'''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ site_name }}{% if title %} — {{ title }}{% endif %}</title>
  <meta name="description" content="GeniusBaby Cosmetics — premium ladies' cosmetics for every skin tone & type.">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{{ url_for('static', filename='css/styles.css') }}" rel="stylesheet">
  <link rel="icon" href="{{ url_for('static', filename='img/favicon.svg') }}" type="image/svg+xml">
</head>
<body>
<nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
  <div class="container">
    <a class="navbar-brand fw-bold" href="{{ url_for('home') }}">GeniusBaby<span class="text-primary">Cosmetics</span></a>
    <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div id="nav" class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto">
        <li class="nav-item"><a class="nav-link" href="{{ url_for('products') }}">Products</a></li>
        <li class="nav-item"><a class="nav-link" href="#contact">Contact</a></li>
      </ul>
      <form class="d-flex" role="search" action="{{ url_for('products') }}">
        <input class="form-control me-2" type="search" name="q" placeholder="Search lipsticks, skincare…" value="{{ request.args.get('q','') }}">
        <button class="btn btn-primary">Search</button>
      </form>
    </div>
  </div>
</nav>

<main class="py-4">
  <div class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="position-fixed top-0 end-0 p-3" style="z-index: 1080;">
          {% for cat, msg in messages %}
            <div class="toast align-items-center text-bg-{{ 'success' if cat=='success' else 'warning' if cat=='warning' else 'danger' if cat=='danger' else 'info' }} border-0 show mb-2">
              <div class="d-flex">
                <div class="toast-body">{{ msg }}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
              </div>
            </div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
</main>

<footer class="border-top py-4 mt-5">
  <div class="container d-flex flex-wrap justify-content-between align-items-center">
    <p class="mb-0 small">&copy; {{ now_year }} {{ site_name }}. All rights reserved.</p>
    <form class="d-flex gap-2" method="post" action="{{ url_for('subscribe') }}">
      <input type="email" name="email" class="form-control form-control-sm" placeholder="Join our newsletter">
      <button class="btn btn-sm btn-outline-primary">Subscribe</button>
    </form>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''
write("templates/base.html", base_html.strip() + "\n")

# ---------------- templates/index.html ----------------
index_html = r'''
{% extends "base.html" %}
{% block content %}
<section class="py-4">
  <div class="p-5 mb-4 bg-light rounded-3">
    <div class="container-fluid py-5">
      <h1 class="display-6 fw-bold">Beauty that loves you back.</h1>
      <p class="col-md-8 fs-5">Clean, vibrant, and designed for every skin tone — discover the GeniusBaby range.</p>
      <a href="{{ url_for('products') }}" class="btn btn-primary btn-lg">Shop Products</a>
    </div>
  </div>
</section>

{% if featured %}
<section class="mb-5">
  <h2 class="h4 mb-3">Featured</h2>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
    {% for p in featured %}
      <div class="col">
        <div class="card h-100">
          <img src="{{ p.image_url or url_for('static', filename='img/placeholder.svg') }}" class="card-img-top" alt="{{ p.name }}">
          <div class="card-body">
            <h3 class="h6 card-title"><a class="text-decoration-none" href="{{ url_for('product_detail', slug_or_id=p.slug) }}">{{ p.name }}</a></h3>
            <p class="mb-1">
              {% if p.sale_price and p.sale_price < p.price %}
                <span class="text-muted text-decoration-line-through">{{ p.price|money }}</span>
                <span class="fw-bold text-danger">{{ p.sale_price|money }}</span>
              {% else %}
                <span class="fw-bold">{{ p.price|money }}</span>
              {% endif %}
            </p>
            <div class="small text-muted">{{ p.brand }} • {{ p.category }}</div>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>
</section>
{% endif %}

<section>
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h2 class="h4 mb-0">Latest arrivals</h2>
    <div>
      <a class="btn btn-sm btn-outline-secondary" href="{{ url_for('products') }}">Browse all</a>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
    {% for p in latest %}
      <div class="col">
        <div class="card h-100">
          <img src="{{ p.image_url or url_for('static', filename='img/placeholder.svg') }}" class="card-img-top" alt="{{ p.name }}">
          <div class="card-body">
            <h3 class="h6 card-title"><a class="text-decoration-none" href="{{ url_for('product_detail', slug_or_id=p.slug) }}">{{ p.name }}</a></h3>
            <p class="mb-1">
              {% if p.sale_price and p.sale_price < p.price %}
                <span class="text-muted text-decoration-line-through">{{ p.price|money }}</span>
                <span class="fw-bold text-danger">{{ p.sale_price|money }}</span>
              {% else %}
                <span class="fw-bold">{{ p.price|money }}</span>
              {% endif %}
            </p>
            <div class="small text-muted">{{ p.brand }} • {{ p.category }}</div>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>
</section>

<section id="contact" class="mt-5">
  <div class="row g-4">
    <div class="col-md-6">
      <h2 class="h4">Contact us</h2>
      <form method="post" action="{{ url_for('contact_submit') }}" class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Name</label>
          <input class="form-control" name="name" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">Email</label>
          <input type="email" class="form-control" name="email" required>
        </div>
        <div class="col-12">
          <label class="form-label">Message</label>
          <textarea class="form-control" name="message" rows="4" required></textarea>
        </div>
        <div class="col-12">
          <button class="btn btn-primary">Send</button>
        </div>
      </form>
    </div>
    <div class="col-md-6">
      <h2 class="h4">About GeniusBaby</h2>
      <p>We make high-performance cosmetics with skin-loving ingredients. Our formulations are tested for comfort, shade range, and lasting wear.</p>
      <ul class="list-unstyled small">
        <li>• Nairobi, Kenya</li>
        <li>• Open Mon–Sat, 9am–6pm</li>
        <li>• Email: hello@geniusbabycosmetics.com</li>
      </ul>
    </div>
  </div>
</section>
{% endblock %}
'''
write("templates/index.html", index_html.strip() + "\n")

# ---------------- templates/products.html ----------------
products_html = r'''
{% extends "base.html" %}
{% block content %}
<div class="d-flex align-items-center justify-content-between">
  <h1 class="h4">Products</h1>
  <div class="text-muted small">{{ total }} results</div>
</div>

<form class="row g-2 my-3">
  <div class="col-md-3">
    <input class="form-control" name="q" value="{{ q }}" placeholder="Search products…">
  </div>
  <div class="col-md-2">
    <select class="form-select" name="category">
      <option value="">All categories</option>
      {% for c in categories %}
        <option value="{{ c }}" {{ 'selected' if c==category else '' }}>{{ c }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="col-md-2">
    <select class="form-select" name="brand">
      <option value="">All brands</option>
      {% for b in brands %}
        <option value="{{ b }}" {{ 'selected' if b==brand else '' }}>{{ b }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="col-md-2">
    <input class="form-control" name="min_price" value="{{ min_price }}" placeholder="Min price">
  </div>
  <div class="col-md-2">
    <input class="form-control" name="max_price" value="{{ max_price }}" placeholder="Max price">
  </div>
  <div class="col-md-1">
    <select class="form-select" name="sort" title="Sort">
      <option value="newest" {{ 'selected' if sort=='newest' else '' }}>Newest</option>
      <option value="price_asc" {{ 'selected' if sort=='price_asc' else '' }}>Price ↑</option>
      <option value="price_desc" {{ 'selected' if sort=='price_desc' else '' }}>Price ↓</option>
      <option value="rating" {{ 'selected' if sort=='rating' else '' }}>Top rated</option>
      <option value="name_asc" {{ 'selected' if sort=='name_asc' else '' }}>Name A–Z</option>
      <option value="name_desc" {{ 'selected' if sort=='name_desc' else '' }}>Name Z–A</option>
    </select>
  </div>
  <div class="col-12 d-flex gap-2">
    <button class="btn btn-primary">Apply</button>
    <a class="btn btn-outline-secondary" href="{{ url_for('products') }}">Reset</a>
  </div>
</form>

<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
  {% for p in items %}
    <div class="col">
      <div class="card h-100">
        <img src="{{ p.image_url or url_for('static', filename='img/placeholder.svg') }}" class="card-img-top" alt="{{ p.name }}">
        <div class="card-body">
          <h3 class="h6 card-title"><a class="text-decoration-none" href="{{ url_for('product_detail', slug_or_id=p.slug) }}">{{ p.name }}</a></h3>
          <p class="mb-1">
            {% if p.sale_price and p.sale_price < p.price %}
              <span class="text-muted text-decoration-line-through">{{ p.price|money }}</span>
              <span class="fw-bold text-danger">{{ p.sale_price|money }}</span>
            {% else %}
              <span class="fw-bold">{{ p.price|money }}</span>
            {% endif %}
          </p>
          <div class="small text-muted">{{ p.brand }} • {{ p.category }}</div>
        </div>
      </div>
    </div>
  {% endfor %}
</div>

{% if pages > 1 %}
<nav class="mt-4">
  <ul class="pagination">
    {% for p in range(1, pages+1) %}
      <li class="page-item {{ 'active' if p==page else '' }}">
        <a class="page-link" href="{{ url_for('products', q=q, category=category, brand=brand, min_price=min_price, max_price=max_price, sort=sort, page=p, per_page=per_page) }}">{{ p }}</a>
      </li>
    {% endfor %}
  </ul>
</nav>
{% endif %}
{% endblock %}
'''
write("templates/products.html", products_html.strip() + "\n")

# ---------------- templates/product_detail.html ----------------
product_detail_html = r'''
{% extends "base.html" %}
{% block content %}
<div class="row g-4">
  <div class="col-md-6">
    <img class="img-fluid rounded border" src="{{ item.image_url or url_for('static', filename='img/placeholder.svg') }}" alt="{{ item.name }}">
  </div>
  <div class="col-md-6">
    <h1 class="h3">{{ item.name }}</h1>
    <div class="mb-2 text-muted">{{ item.brand }} • {{ item.category }}</div>
    <div class="h5">
      {% if item.sale_price and item.sale_price < item.price %}
        <span class="text-muted text-decoration-line-through">{{ item.price|money }}</span>
        <span class="fw-bold text-danger">{{ item.sale_price|money }}</span>
      {% else %}
        <span class="fw-bold">{{ item.price|money }}</span>
      {% endif %}
    </div>
    {% if item.rating %}
      <div class="mb-3 small">Rating: {{ item.rating }} / 5</div>
    {% endif %}
    <p>{{ item.description }}</p>
    {% if item.ingredients %}
      <div class="small text-muted"><strong>Ingredients:</strong> {{ item.ingredients }}</div>
    {% endif %}
    {% if item.skin_type %}
      <div class="small text-muted"><strong>Skin type:</strong> {{ item.skin_type }}</div>
    {% endif %}
    <div class="mt-3">
      {% if item.stock and item.stock > 0 %}
        <span class="badge text-bg-success">In stock</span>
      {% else %}
        <span class="badge text-bg-secondary">Out of stock</span>
      {% endif %}
    </div>
  </div>
</div>

{% if related %}
<hr class="my-5">
<h2 class="h5 mb-3">You may also like</h2>
<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
  {% for p in related %}
    <div class="col">
      <div class="card h-100">
        <img src="{{ p.image_url or url_for('static', filename='img/placeholder.svg') }}" class="card-img-top" alt="{{ p.name }}">
        <div class="card-body">
          <h3 class="h6 card-title"><a class="text-decoration-none" href="{{ url_for('product_detail', slug_or_id=p.slug) }}">{{ p.name }}</a></h3>
          <div class="small text-muted">{{ p.brand }} • {{ p.category }}</div>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
{% endif %}
{% endblock %}
'''
write("templates/product_detail.html", product_detail_html.strip() + "\n")

# ---------------- templates/admin_new_product.html ----------------
admin_new_product_html = r'''
{% extends "base.html" %}
{% block content %}
<h1 class="h4">New product</h1>
<form method="post" class="row g-3">
  <div class="col-md-6">
    <label class="form-label">Name</label>
    <input class="form-control" name="name" required>
  </div>
  <div class="col-md-6">
    <label class="form-label">Slug (optional)</label>
    <input class="form-control" name="slug" placeholder="auto-generated from name">
  </div>
  <div class="col-md-4">
    <label class="form-label">Brand</label>
    <input class="form-control" name="brand">
  </div>
  <div class="col-md-4">
    <label class="form-label">Category</label>
    <input class="form-control" name="category">
  </div>
  <div class="col-md-2">
    <label class="form-label">Price</label>
    <input class="form-control" name="price" value="1499" required>
  </div>
  <div class="col-md-2">
    <label class="form-label">Sale price</label>
    <input class="form-control" name="sale_price" value="0">
  </div>
  <div class="col-12">
    <label class="form-label">Image URL</label>
    <input class="form-control" name="image_url" placeholder="https://...">
  </div>
  <div class="col-12">
    <label class="form-label">Description</label>
    <textarea class="form-control" rows="4" name="description"></textarea>
  </div>
  <div class="col-12">
    <label class="form-label">Ingredients</label>
    <textarea class="form-control" rows="3" name="ingredients"></textarea>
  </div>
  <div class="col-md-3">
    <label class="form-label">Skin type</label>
    <input class="form-control" name="skin_type" placeholder="All / Dry / Oily ...">
  </div>
  <div class="col-md-3">
    <label class="form-label">Rating</label>
    <input class="form-control" name="rating" value="4.8">
  </div>
  <div class="col-md-3">
    <label class="form-label">Stock</label>
    <input class="form-control" name="stock" value="100">
  </div>
  <div class="col-md-3 form-check mt-4">
    <input class="form-check-input" type="checkbox" name="is_featured" id="featured">
    <label class="form-check-label" for="featured">Featured</label>
  </div>
  <div class="col-12">
    <button class="btn btn-primary">Create</button>
  </div>
</form>
{% endblock %}
'''
write("templates/admin_new_product.html", admin_new_product_html.strip() + "\n")

# ---------------- static/css/styles.css ----------------
styles_css = r'''
:root { --gbc-pink: #ff5fa2; }
.card img { object-fit: cover; height: 220px; }
'''
write("static/css/styles.css", styles_css.strip() + "\n")

# ---------------- static/js/main.js ----------------
main_js = r'''
// Placeholder for future enhancements (analytics, cart, etc.)
document.addEventListener("DOMContentLoaded", () => {
  // Auto-hide toasts after 3s
  const toasts = document.querySelectorAll(".toast");
  setTimeout(() => toasts.forEach(t => t.classList.remove("show")), 3000);
});
'''
write("static/js/main.js", main_js.strip() + "\n")

# ---------------- static/img/placeholder.svg ----------------
placeholder_svg = r'''
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800">
  <defs>
    <linearGradient id="g" x1="0" x2="1">
      <stop offset="0" stop-color="#ffd1e6"/>
      <stop offset="1" stop-color="#ffeef6"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <text x="50%" y="50%" text-anchor="middle" font-size="42" fill="#ff5fa2" font-family="Arial, Helvetica">GeniusBaby Cosmetics</text>
</svg>
'''
write("static/img/placeholder.svg", placeholder_svg.strip() + "\n")
write("static/img/favicon.svg", placeholder_svg.strip() + "\n")
