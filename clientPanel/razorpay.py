import razorpay

# Razorpay API Keys
RAZORPAY_KEY_ID = "rzp_test_TaDJtEHooM9W9G"
RAZORPAY_KEY_SECRET = "VGvaV62OJdjpVsFhlI7aQcIK" 


# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def razorpay_order(amount):

    order_obj = {
        "amount": int(amount * 100),   # ₹590 → 59000 paise
        "currency": "INR",
        "receipt": "movie_booking"
    }

    razorpay_order = razorpay_client.order.create(data=order_obj)

    return razorpay_order
