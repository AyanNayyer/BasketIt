from flask import render_template, request, session, redirect,flash
from flask import current_app as app
from applications.database import db
from applications.models import User, Product, Section, Cart, PromoCode
from passlib.hash import pbkdf2_sha256 as passhash
from datetime import datetime

@app.route("/")
def home():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        products = Product.query.all()
        sections=Section.query.all()
        if user.is_admin:
            is_admin = True
        else:
            is_admin = False
        return render_template("home.html", user=session["user"], signed=True, is_admin=is_admin, products=products,sections=sections)
    else:
        return render_template("home.html", user="", signed=False, is_admin=False)

from flask import request, flash, redirect, render_template


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        if not is_valid_password(password):
            flash("Invalid password. Password must contain at least one number, one letter, one special character, and be at least 8 characters long.", "error")
            return redirect("/register") 

        password = passhash.hash(password)
        user = User.query.filter_by(name=username).first()
        if user is not None:
            flash("The user already exists. Please login.")
            return redirect("/login")

        user = User(name=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        session["user"] = username
        flash("Registration successful.", "success")
        return redirect("/")

def is_valid_password(password):
    if len(password) < 8:
        return False

    has_number = any(char.isdigit() for char in password)

    has_letter = any(char.isalpha() for char in password)

    special_chars = "!@#$%^&*()_+{}[]:;<>,.?~\\-"
    has_special_char = any(char in special_chars for char in password)

    return has_number and has_letter and has_special_char

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(name = username).first()
        if user is None:
            flash("User not found. Please register.")
            return redirect("/register")
        if not passhash.verify(password, user.password):
            flash("Invalid credentials. Please try again.")
            return redirect("/login")
        session["user"] = username
        return redirect("/")
    
@app.route("/manager_login", methods=["GET", "POST"])
def manager_login():
    if request.method == "GET":
        return render_template("manager_login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(name=username, is_admin=True).first()
        
        if user is None:
            flash("Manager not found!")
            return redirect("/manager_login")
        if not passhash.verify(password, user.password):
            flash("Invalid Credentials, Please try again!")
            return redirect("/manager_login")
        
        session["user"] = username
        return redirect("/dashboard")
    
''' To display Search result on the home page itself with layout
@app.route("/search", methods=["POST"])
def search():
    
    search_query = request.form.get("search_query", "")
    products = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
    sections = Section.query.filter(Section.name.ilike(f"%{search_query}%")).all()
    submitted = True if search_query else False

    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        is_admin = user.is_admin if user else False
        return render_template("home.html", user=session["user"], signed=True, is_admin=is_admin, products=products,sections=sections,submitted=submitted)
    else:
        return render_template("home.html", user="", signed=False, is_admin=False, products=products,sections=sections,submitted=submitted)
    '''
        
@app.route('/search', methods=['GET'])
def search():
    criteria = request.args.get('criteria')
    query = request.args.get('query')

    if not criteria or not query:
        return render_template('search.html', search_results=[], message="Please select a criteria and enter a query.")

    search_results = []

    if criteria == 'products':
        search_results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    elif criteria == 'sections':
        search_results = Section.query.filter(Section.name.ilike(f'%{query}%')).all()
    elif criteria == 'rate':
        search_results = Product.query.filter(Product.rate == float(query)).all()
    elif criteria == 'stock':
        search_results = Product.query.filter(Product.stock == int(query)).all()
    elif criteria == 'expiry_date':
        p_exp=datetime.strptime(query, "%Y-%m-%d").date()
        search_results = Product.query.filter(Product.expiry_date == p_exp).all()
    elif criteria == 'manufacture_date':
        p_mfg=datetime.strptime(query, "%Y-%m-%d").date()
        search_results = Product.query.filter(Product.manufacture_date == p_mfg).all()

    return render_template('search.html', search_results=search_results)


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            if request.method == "POST":
                search_query = request.form.get("search_query", "")
                products = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
                sections = Section.query.filter(Section.name.ilike(f"%{search_query}%")).all()
            else:
                products = Product.query.all()
                sections = Section.query.all()
            return render_template("manager_dashboard.html", products=products, user=session["user"],section=sections, sections=sections)
    return redirect("/")

@app.route("/add_product", methods = ["GET", "POST"])
def add_product():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            if request.method == "GET":
                sections = Section.query.all()
                return render_template("add_product.html", sections=sections)
            elif request.method == "POST":
                name = request.form["name"]
                stock = request.form["stock"]
                manufacture_date = request.form["manufacture_date"]
                p_mfg=datetime.strptime(manufacture_date, "%Y-%m-%d").date()
                expiry_date = request.form["expiry_date"]
                p_exp=datetime.strptime(expiry_date , "%Y-%m-%d").date()
                rate = request.form["rate"]
                section_id = int(request.form["section_id"])
                img = request.files["img"]
                product = Product(name=name, stock=stock, owner=user.id, section_id=section_id,manufacture_date=p_mfg,expiry_date=p_exp,rate=rate)
                if not section_id:
                    flash('Please select a section')
                    return render_template("add_product.html")    
                db.session.add(product)
                db.session.commit()
                img.save("./static/products/" + str(product.id) + ".png")
                return redirect("/dashboard")
    return redirect("/")


@app.route("/delete_product/<product_id>", methods = ["GET", "POST"])
def delete_product(product_id):
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            if request.method == "GET":
                return render_template("delete_product.html")
            elif request.method == "POST":
                if "yes" in request.form:
                    product = Product.query.filter_by(id = product_id).first()
                    db.session.delete(product)
                    db.session.commit()
                    return redirect("/dashboard")
                else:
                    return redirect("/dashboard")
    return redirect("/")

@app.route("/edit_product/<product_id>", methods = ["GET", "POST"])
def edit_product(product_id):
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            product = Product.query.filter_by(id = product_id).first()     
            if request.method == "GET":
                return render_template("edit_product.html", product=product)
            elif request.method == "POST":
                name = request.form["name"]
                stock = request.form["stock"]
                manufacture_date = request.form["manufacture_date"]
                p_mfg=datetime.strptime(manufacture_date, "%Y-%m-%d").date()
                expiry_date = request.form["expiry_date"]
                p_exp=datetime.strptime(expiry_date , "%Y-%m-%d").date()
                rate = request.form["rate"]
                img = request.files["img"]
                if name:
                    product.name = name
                if stock:
                    product.stock = stock
                if rate:
                    product.rate= rate
                if manufacture_date:
                    product.manufacture_date= p_mfg
                if expiry_date:
                    product.expiry_date= p_exp
                db.session.commit()
                if img:
                    img.save("./static/products/" + str(product.id) + ".png")
                return redirect("/dashboard")
    return redirect("/")

@app.route("/add_section", methods=["GET", "POST"])
def add_section():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            if request.method == "GET":
                return render_template("add_section.html")
            elif request.method == "POST":
                section_name = request.form.get("section_name")
                if section_name=="":
                    flash("Section name can't be empty!" )
                    return render_template("add_section.html")
                new_section = Section(name=section_name)
                db.session.add(new_section)
                db.session.commit()
                return redirect("/dashboard")
    return render_template("add_section.html")

@app.route("/delete_section", methods=["GET"])
def display_delete_section():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            sections = Section.query.all()
            return render_template("delete_section.html", sections=sections)
        return redirect("/")


@app.route("/delete_section", methods=["POST"])
def delete_section():
    try:
        if "user" in session:
            user = User.query.filter_by(name=session["user"]).first()
            if user.is_admin:
                section_id = int(request.form.get("section_id"))
                section = Section.query.get(section_id)
                if section:
                    db.session.delete(section)
                    db.session.commit()
    except:
        return redirect("/dashboard")
    return redirect("/dashboard")

    
@app.route("/edit_section", methods=["GET", "POST"])
def display_edit_section():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.is_admin:
            if request.method == "POST":
                section_id = request.form["section_id"]
                new_section_name = request.form["name"]

                if not new_section_name.strip():
                    flash("Section name cannot be blank.", "error")
                else:
                    section = Section.query.get(section_id)
                    if section:
                        section.name = new_section_name
                        db.session.commit()
                        flash("Section updated successfully.", "success")
                        return redirect("/dashboard")

            sections = Section.query.all()
            return render_template("edit_section.html", sections=sections,section=sections)
    return redirect("/")
    
@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user:
            product = Product.query.get(product_id)
            if product:
                cart = Cart.query.filter_by(user_id=user.id, product_id=product.id).first()
                quantity_str = request.form.get("quantity", "")
                
                try:
                    quantity = int(quantity_str)
                    if quantity <= 0:
                        raise ValueError
                except ValueError:
                    flash("Please enter a valid quantity.", "error")
                    return redirect("/")
                
                if quantity > product.stock:
                    flash("Sorry, the requested quantity exceeds the available stock.", "error")
                    return redirect("/")

                if cart:
                    cart.quantity += quantity
                else:
                    cart = Cart(user_id=user.id, product_id=product.id, quantity=quantity)
                try:    
                    if cart.quantity > cart.product.stock:
                        flash("Please select less quantity or Max quantity already in stock.")
                        return redirect("/")
                except:
                    pass
                    
                db.session.add(cart)
                db.session.commit()

                flash(f"{product.name} added to cart.", "success")
                return redirect("/")
    
    flash("You need to be logged in as a user to add products to the cart.", "error")
    return redirect("/login")

@app.route("/cart")
def cart():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        cart_contents = get_cart_contents(user.id)
        if user:
            cart_contents = Cart.query.filter_by(user_id=user.id).all()

            total_amount = 0.0
            try:
                for item in cart_contents:
                    total_amount += item.product.rate * item.quantity

                return render_template("cart.html", cart_contents=cart_contents, total_amount=total_amount, item=item,cart_items=cart_contents)
            except:
                return render_template("cart.html", cart_contents=cart_contents, total_amount=total_amount,cart_items=cart_contents)

    return redirect("/login")

@app.route("/update_quantity/<int:product_id>", methods=["POST"])
def update_quantity(product_id):
    if "user" not in session:
        flash("Please log in to update the cart.")
        return redirect("/login")

    user = User.query.filter_by(name=session["user"]).first()
    cart = Cart.query.filter_by(user_id=user.id, product_id=product_id).first()

    if not cart:
        flash("Product not found in cart.")
        return redirect("/cart")

    new_quantity_str = request.form.get("quantity", "")

    new_quantity = int(new_quantity_str)
    if new_quantity < 1 or new_quantity > cart.product.stock:
        flash("Please enter a valid quantity.")
        return redirect("/cart")

    cart.quantity = new_quantity
    db.session.commit()

    flash("Quantity updated successfully.")
    return redirect("/cart")


@app.route("/remove_product/<int:product_id>", methods=["POST"])
def remove_product(product_id):
    if "user" not in session:
        flash("Please log in to update the cart.")
        return redirect("/login")

    user = User.query.filter_by(name=session["user"]).first()
    cart = Cart.query.filter_by(user_id=user.id, product_id=product_id).first()

    if not cart:
        flash("Product not found in cart.")
        return redirect("/cart")

    db.session.delete(cart)
    db.session.commit()

    flash("Product removed from cart.")
    return redirect("/cart")

@app.route("/apply_promo_code", methods=["POST"])
def apply_promo_code():
    promo_code = request.form.get("promo_code", "").strip()
    user = User.query.filter_by(name=session["user"]).first()
    
    if user.first_purchase_completed:
        flash("Promo code can only be applied to your first purchase.", "warning")
        return redirect("/cart")

    promo_code_data = PromoCode.query.filter_by(code=promo_code).first()
    total_amount=0.0
    cart_contents = Cart.query.filter_by(user_id=user.id).all()
    for item in cart_contents:
        total_amount += item.product.rate * item.quantity

    if promo_code_data:
        discount_percentage = promo_code_data.discount_percentage
        cart_contents = get_cart_contents(user.id)
        total_amount = sum(item.product.rate * item.quantity for item in cart_contents)
        updated_total_amount = round(total_amount * (1 - discount_percentage / 100))

        return render_template("cart.html", cart_contents=cart_contents, total_amount=updated_total_amount, updated_total_amount=updated_total_amount,item=item,cart_items=cart_contents)

    else:
        flash("Invalid promo code. Please enter a valid promo code.", "warning")
        return redirect("/cart")
    
def get_cart_contents(user_id):
    cart_contents = Cart.query.filter_by(user_id=user_id).all()
    return cart_contents

@app.route('/buy_now', methods=['POST'])
def buy_now():
    user = User.query.filter_by(name=session["user"]).first()
    cart_contents = get_cart_contents(user.id)

    for cart_item in cart_contents:
        product_id = cart_item.product.id 
        quantity = cart_item.quantity 

        product = Product.query.get(product_id)

        if product.stock >= quantity:
            product.stock -= quantity
            db.session.commit()
        else:
            flash(f"Sorry, {product.name} is out of stock. Please update your cart.", "error")
            return redirect('/cart')
        
    Cart.query.filter_by(user_id=user.id).delete()
    user.first_purchase_completed=True
    db.session.commit()

    flash("Products purchased successfully.", "success")
    return redirect('/')

