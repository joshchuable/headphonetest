import sys
import os
from flask import Flask, request, render_template, make_response, url_for, redirect
from io import StringIO
import datetime
import stripe
from paypal import PayPalConfig
from paypal import PayPalInterface
from flask_mail import Mail, Message
from pscripts.send_email import ContactForm

#Paypal configs
config = PayPalConfig(API_USERNAME = "admin-facilitator_api1.Rialto Exchange.com",
                      API_PASSWORD = "VHD5LBSTVY5F2LVY",
                      API_SIGNATURE = "AFcWxV21C7fd0v3bYYYRCpSSRl31A31AGwDGKoQXB-ZlN1VRvKP2zDyu",
                      DEBUG_LEVEL=1)

interface = PayPalInterface(config=config)

 #Stripe Configs
stripe_keys = {
    'secret_key': "sk_test_BnQz5NQauCGFT5lWsQROeTX6",
    'publishable_key': "pk_test_U2NHMtMm8NmjPT9m8ZWyjf8t"
}

stripe.api_key = stripe_keys['secret_key']

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

namelist = {"headphones": "The Rialto Headphone"}
pricelist = {"headphones": 24.99}

@app.route("/")
def index():
    product = "headphones"
    name = productname(product)
    productprice = price(product)
    return render_template("home.html", name=name, price=productprice, product=product)

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

def productname(product):
    return namelist[product]

def price(product):
    return pricelist[product]

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

@app.route("/charge/stripe/<amount>", methods=['POST'])
def charge(amount):
    # Amount in cents
    token = request.form['stripeToken']
    dollar_amount = int(amount)/100
    country = request.form['stripeShippingAddressCountry']
    state = request.form['stripeShippingAddressState']
    customer = stripe.Customer.create(
                source=token
            )
    if country not in ["US", "United States"] or state in ['Alaska','AK','Hawaii','HI']:
        return render_template('error.html', error="Sorry, we only take orders from the continental U.S. at this time. Your card will not be charged. For international inquiries, please email us at contact@Rialto Exchange.com")
    else:
        try:
            charge = stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency='usd',
            )

            return render_template('error.html',error="Whoops, we're all out of stock. Send us a message at info@Rialto Exchange.com and we'll let you know when we have more in store!")
        except stripe.CardError:
            return render_template('error.html', error="Your card swas declined. Please try again or call your credit card company.")

@app.route("/paypal/redirect/<amount>")
def paypal_redirect(amount):
    return render_template('error.html',error="Whoops, we're all out of stock. Leave us your email and we'll let you know when we restock!")

@app.route("/paypal/confirm")
def paypal_confirm():
    getexp_response = interface.get_express_checkout_details(token=request.args.get('token', ''))

    if getexp_response['ACK'] == 'Success':
        return """
            Everything looks good! <br />
            <a href="%s">Click here to complete the payment.</a>
        """ % url_for('paypal_do', token=getexp_response['TOKEN'])
    else:
        return """
            Oh noes! PayPal returned an error code. <br />
            <pre>
                %s
            </pre>
            Click <a href="%s">here</a> to try again.
        """ % (getexp_response['ACK'], url_for('index'))


@app.route("/paypal/do/<string:token>")
def paypal_do(token):
    getexp_response = interface.get_express_checkout_details(token=token)
    kw = {
        'amt': getexp_response['AMT'],
        'paymentaction': 'Sale',
        'payerid': getexp_response['PAYERID'],
        'token': token,
        'currencycode': getexp_response['CURRENCYCODE']
    }
    interface.do_express_checkout_payment(**kw)

    return redirect(url_for('paypal_status', token=kw['token']))

@app.route("/paypal/status/<string:token>")
def paypal_status(token):
    checkout_response = interface.get_express_checkout_details(token=token)

    if checkout_response['CHECKOUTSTATUS'] == 'PaymentActionCompleted':
        # Here you would update a database record.
        return """
            Awesome! Thank you for your %s %s purchase.
        """ % (checkout_response['AMT'], checkout_response['CURRENCYCODE'])
    else:
        return """
            Oh no! PayPal doesn't acknowledge the transaction. Here's the status:
            <pre>
                %s
            </pre>
        """ % checkout_response['CHECKOUTSTATUS']

@app.route("/paypal/cancel")
def paypal_cancel():
    return redirect(url_for('index'))

@app.route("/terms/")
def terms():
    return render_template("terms/terms.html")

if __name__ == "__main__":
	app.run(debug=True)
