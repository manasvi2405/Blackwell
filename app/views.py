
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator
from .models import Product,ProductCategory
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from user.models import Cart,CartItem,Address,Order,OrderItem
from django.views.decorators.csrf import csrf_exempt
import razorpay


# Create your views here.
def home(request):
    products = Product.objects.all()[0:4]

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_count = sum(item.quantity for item in cart.items.all())
        else:
            cart_count = 0
    else:
        cart_count = 0

    return render(request, 'home.html', {
        'products': products,
        'cart_count': cart_count
    })

def about(request):
    return render(request,'about.html',{})

def cart(request):
    return render(request,'cart.html',{})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # 1. Save the data to the database
            contact_instance = form.save()


            # 2. Extract data for the email
            user_name = form.cleaned_data['name']
            user_email = form.cleaned_data['email']
            user_message = form.cleaned_data['message']
           
            # 3. Send the email
            try:
                send_mail(
                subject=f'New Contact Message from {user_name}',
                message=f'Name: {user_name}\nEmail: {user_email}\n\nMessage:\n{user_message}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],   # your email
                fail_silently=False
                )

                send_mail(
                subject=f'Thank You, {user_name}!',
                message=f'Hi {user_name},\n\nWe have received your message. We will get back to you shortly.\n\nBest Regards,\nTeam BlackWell',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email],
                fail_silently=False)
            except Exception as e:
                print(f"Email sending failed: {e}")
           
            # 4. Add a success message to display on the page
            messages.success(request, "Your message has been sent successfully! Check your email for confirmation.")
       
            return redirect('contact')


    else:
    # GET request: Display an empty form
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})



def shop(request,cat):
    category = ProductCategory.objects.get(id=cat)
    data = Product.objects.filter(category=cat)
    p = Paginator(data,8)
    page_num=request.GET.get('page')
    product=p.get_page(page_num)
    return render(request,'shop.html',{'products':product,'category':category})

def product(request,id):
    product=Product.objects.get(id=id)
    category=product.category
    category_products=Product.objects.filter(category=category).exclude(id=id)
    return render(request,'product.html',{'product':product,'category_products':category_products})

def shopbycategory(request,cat):
    parentcategory=ProductCategory.objects.get(id=cat)
    category_ids = parentcategory.subcategories.all().values_list('id', flat=True)
    all_ids = [parentcategory.id] + list(category_ids)
    # Filter products
    data = Product.objects.filter(category_id__in=all_ids)
    p=Paginator(data,8)
    page_num=request.GET.get('page')
    product=p.get_page(page_num)
    return render(request,'shop.html',{'products':product ,'category':parentcategory})



def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)

    # ✅ Logged-in user
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

    # ✅ Guest user (session)
    else:
        cart = request.session.get('cart', {})

        item_id = str(item_id)
        if item_id in cart:
            cart[item_id] += 1
        else:
            cart[item_id] = 1

        request.session['cart'] = cart

    return redirect('view_cart')   

def view_cart(request):

    items = []
    total_price = 0

    # ✅ Logged-in user
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

        for item in cart.items.all():
            total_price += item.total_price
            items.append(item)

    # ✅ Guest user (session)
    else:
        session_cart = request.session.get('cart', {})

        for product_id, quantity in session_cart.items():
            product = Product.objects.get(id=product_id)

            total = quantity * product.selling_price
            total_price += total

            items.append({
                'id': product.id,  # 👈 IMPORTANT (used in template)
                'product': product,
                'quantity': quantity,
                'total_price': total
            })

    return render(request, 'cart.html', {
        'items': items,
        'total_price': total_price
    })


def update_cart_quantity(request, action, item_id):

    # ✅ Logged-in user → DB
    if request.user.is_authenticated:
        cart_item = get_object_or_404(
            CartItem, id=item_id, cart__user=request.user
        )

        if action == 'increase':
            cart_item.quantity += 1

        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1

        elif action == 'decrease' and cart_item.quantity == 1:
            cart_item.delete()
            return redirect('view_cart')

        cart_item.save()

    # ✅ Guest user → session
    else:
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        if item_id in cart:
            if action == 'increase':
                cart[item_id] += 1

            elif action == 'decrease':
                if cart[item_id] > 1:
                    cart[item_id] -= 1
                else:
                    del cart[item_id]

        request.session['cart'] = cart

    return redirect('view_cart')


def remove_from_cart(request, item_id):

    # ✅ Logged-in user → DB
    if request.user.is_authenticated:
        cart_item = get_object_or_404(
            CartItem, id=item_id, cart__user=request.user
        )
        cart_item.delete()

    # ✅ Guest user → session
    else:
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        if item_id in cart:
            del cart[item_id]

        request.session['cart'] = cart

    return redirect('view_cart')

@login_required(login_url='login')
def checkout_view(request):
    user = request.user
   
    # 1. Get the User's Cart
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all() # Uses the related_name 'items' from CartItem
    except Cart.DoesNotExist:
        return redirect('cart_summary') # Redirect if cart is empty


    # 2. Fetch Saved Addresses
    addresses = Address.objects.filter(user=user).order_by('-is_default')
   
    # 3. Calculate Totals (using your existing @property)
    total_amount = cart.total_price


    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'total_amount': total_amount,
    }
   
    return render(request, 'checkout.html', context)

@login_required
def process_order(request):
    #validate address
    if request.method=='POST':
        user=request.user
        address_id=request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        #validate address
        if not address_id:
            return redirect('checkout_view')
        shipping_address=get_object_or_404(Address,id=address_id,user=user)
        #get user cart
        cart=get_object_or_404(Cart,user=user)
        if not cart.items.exists():
            return redirect('view_cart')
        #create the order object
        order=Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_amount=cart.total_price,
            status='Pending',
            payment_method=payment_method
        )
     #Snapshot cartitems into orderitems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.quantity
            )
        if payment_method == "cod":

            return render(request, "success.html", {
                "order": order
            })
        else:
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(order.total_amount * 100), # Amount in paise
                "currency": "INR",
                "receipt": f"order_{order.id}"
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            return redirect('payment_page', order_id=order.id)

    return render(request, 'checkout.html', {})

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
   
    context = {
        'order': order,
        'razorpay_key_id': settings.RAZOR_PAY_KEY_ID, # Store this in settings.py
        'amount_in_paise': int(order.total_amount * 100),
        'currency': 'INR',
        'callback_url': "http://127.0.0.1:8000/payment/verify/", # Your verification URL
    }
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_verify(request):
    if request.method == "POST":
        # 1. Extract data from Razorpay's callback
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')


        # 2. Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))


        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }


        try:
            # 3. Verify the signature
            client.utility.verify_payment_signature(params_dict)
           
            # 4. Success: Update Order in Database
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.is_paid = True
            order.razorpay_payment_id = payment_id
            order.status = 'Packed' # Or your desired next status
            order.save()


            # 5. Clear the User's Cart
            # We delete the CartItems, keeping the Cart object itself for future use
            Cart.objects.get(user=order.user).items.all().delete()


            return render(request, 'success.html', {'order': order})


        except razorpay.errors.SignatureVerificationError:
            # 6. Failure: Signature mismatch
            return render(request, 'failure.html', {'error': 'Payment verification failed.'})
        except Order.DoesNotExist:
            return render(request, 'failure.html', {'error': 'Order not found.'})


    return redirect('home')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["Pending", "Packed"]:
        order.status = "Cancelled"
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect('track_order')


