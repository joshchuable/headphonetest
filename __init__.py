import sys
import os
from flask import Flask, request, render_template, make_response, url_for, redirect
from io import StringIO
import datetime
from flask_mail import Mail, Message
from pscripts.send_email import ContactForm

app = Flask(__name__)
app.secret_key = 'the_R4nD0M_Things___4keys--true'
# Email Configs
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'admin@Rialto Exchange.com'
app.config['MAIL_PASSWORD'] = 'taoist-terrier-sleeve-tingly-debate'
# Mailer
mail = Mail(app)

namelist = {"headphones": "The Rialto Headphone Stand"}
pricelist = {"headphones": 24.99}

@app.route("/")
def index():
    product = "headphones"
    name = productname(product)
    productprice = price(product)
    return render_template("home.html", name=name, price=productprice, product=product)

# Individual test product pages
@app.route("/prod/<product>")
def prod(product):
    name = productname(product)
    productprice = price(product)
    return render_template("home.html", name=name, price=productprice, product=product)

@app.route('/checkout/<product>')
def checkout(product):
    section4 = product + "/" + product + "_4" + ".html"
    name = productname(product)
    productprice = price(product)
    return render_template("checkout/checkout.html",section4=section4, name=name, price=productprice, product=product)

@app.route('/buy/<product>')
def buy(product):
    section4 = product + "/" + product + "_4" + ".html"
    name = productname(product)
    return render_template("error.html",error="Whoops, we're all out of stock. Leave us your email and we'll let you know when we restock!", name=name, product=product)


@app.route('/contact', methods=['POST','GET'])
def contact():
  form = ContactForm()
  if request.method == 'POST':
    if form.validate() == False:
        return 'Please fill out all sections of the form and resubmit.'
    else:
        msg = Message(form.subject.data, sender='admin@Rialto Exchange.com', recipients=['admin@Rialto Exchange.com','rye@Rialto Exchange.com'])
        msg.body = """
        From: %s <%s>
        %s
        """ % (form.name.data, form.email.data, form.message.data)
        mail.send(msg)

        return 'Message sent! Hit back to return to the site.'

  else:
    return render_template('contact/contact.html', form=form)

@app.route("/terms/")
def terms():
    product="headphones"
    return render_template("terms/terms.html", product=product)

#helper functions
def productname(product):
    return namelist[product]

def price(product):
    return pricelist[product]

#For future development. This code should take multiple products to put on the home page.
#@app.route("/")
#def index():
#    products = []
#    i = 0
#    while i <= 3:
#        for key in namelist:
#            products.append(key)
#            i = i + 1
#    product1 = products[1]
#    product2 = products[2]
#    product3 = products[3]
#    productname1 = productname(product1)
#    productname2 = productname(product2)
#    productname3 = productname(product3)
#    price1 = price(product1)
#    price2 = price(product2)
#    price3 = price(product3)
#    section1 = product1 + "/" + product1 + "_4" + ".html"
#    section2 = product2 + "/" + product2 + "_4" + ".html"
#    section3 = product3 + "/" + product3 + "_4" + ".html"
#    return render_template("home3.html", section1=section1, product1=product1)

if __name__ == "__main__":
	app.run(debug=True)
