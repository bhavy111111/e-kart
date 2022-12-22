from django.shortcuts import render,redirect , get_object_or_404
from store.models import Product
from .models import Cart,CartItem
from django.http import HttpResponse
# Create your views here.
def cart(request , total = 0 , quantity = 0 , cart_items=None):
    try:
        cart = Cart.objects.get(cart_id = cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart , is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax = (20* total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity' : quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
        }
    return render(request,'store/cart.html',context)
#Request- Session key

def cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id = product_id)
    product_variation=[]
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation  = Variation.objects.get(product = product , variation_category__iexact =key , variation_value__iexact= value)
                product_variation.append(variation)
            except:
                pass

        '''
        color = request.POST['color']
        size = request.POST['size']
        print(color,size)
        '''
    '''
    return HttpResponse(color +''+size)
    '''
    #product = Product.objects.get(id = product_id)

    try:
        cart = Cart.objects.get(cart_id = cart_id(request)) # get the cart using current session _id
    except CartItem.DoesNotExist:
        raise 'error'
        '''
        cart = Cart.objects.create(
        cart_id = cart_id(request)
        )
        '''
    cart.save()
    #In one cart there can be multiple product items

    try:
        cart_item = CartItem.objects.get(product = product , cart = cart)
        #++1 increment
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
        product = product,
        quantity = 1,
        cart=cart,
        )
        cart_item.save()
    '''
    return HttpResponse(cart_item.quantity)
    exit()
    '''
    return redirect('cart')
def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id = cart_id(request))
    product = get_object_or_404(Product , id = product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id = cart_id(request))
    product = get_object_or_404(Product , id = product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')
