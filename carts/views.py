from django.shortcuts import render,redirect , get_object_or_404
from store.models import Product , Variation
from .models import Cart,CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def cart_id(request):
    cart = request.session.session_key
    print(cart)

    if not cart:
        cart = request.session.create()
    return cart

def cart(request , total = 0 , quantity = 0 , cart_items=None):
    try:
        tax = 0
        grand_total=0
        #For Logged in users
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user= request.user , is_active=True)
            #for non logged in users
        else:
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

def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id) #get the product
    #First check authentictation
    if current_user.is_authenticated:
        print('Product',product)
        product_variation=[]
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                print(key,value)
                try:
                    variation  = Variation.objects.get(product = product , variation_category__iexact =key , variation_value__iexact= value)
                    #variation  = Variation.objects.get(product = product)
                    product_variation.append(variation)
                except:
                    pass

            '''
            color = request.POST['color']
            size = request.POST['size']
            print(color,size)
            '''

        #Checking with same product id and cart id which is session id  , cart item exist or not
        is_cart_item_exists = CartItem.objects.filter(product = product,user  = current_user).exists()
        #print(is_cart_item_exists)
        if is_cart_item_exists:
            #cart_item = CartItem.objects.get(product = product , cart = cart)
            cart_item = CartItem.objects.filter(product = product ,user = current_user)

            empty_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                empty_list.append(list(existing_variation))
                id.append(item.id)
            #Multiple Variation Loop
            if(product_variation in empty_list):
                #Increase cart quantity
                index = empty_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product , id =item_id)
                item.quantity +=1
                item.save()
            else:
                item = CartItem.objects.create(product = product , quantity = 1 ,user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            user=current_user,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        '''
        return HttpResponse(cart_item.quantity)
        exit()
        '''
        return redirect('cart')
    #If user not aur=authenticated
    else:
        print('Product',product)
        product_variation=[]
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                print(key,value)
                try:
                    variation  = Variation.objects.get(product = product , variation_category__iexact =key , variation_value__iexact= value)
                    #variation  = Variation.objects.get(product = product)
                    print('Variations',variation)
                    product_variation.append(variation)
                    print(product_variation)
                except:
                    pass

            '''
            color = request.POST['color']
            size = request.POST['size']
            print(color,size)
            '''

        try:
            cart = Cart.objects.get(cart_id = cart_id(request))
            print(cart) # get the cart using current session _id
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
            cart_id = cart_id(request)
            )
        cart.save()

        #Checking with same product id and cart id which is session id  , cart item exist or not
        is_cart_item_exists = CartItem.objects.filter(product = product,cart=cart).exists()
        #print(is_cart_item_exists)
        if is_cart_item_exists:
            #cart_item = CartItem.objects.get(product = product , cart = cart)
            cart_item = CartItem.objects.filter(product = product , cart=cart)
            #existing variations - databse
            #current variation - database
            # item_id - database
            #1 . if current variation is inside existing variation will update the quantity number
            empty_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                empty_list.append(list(existing_variation))
                id.append(item.id)
            print(id)
            print(empty_list)
            #print(product_variation)
            #Multiple Variation Loop
            if(product_variation in empty_list):
                #Increase cart quantity
                index = empty_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product , id =item_id)
                item.quantity +=1
                item.save()
            else:
                item = CartItem.objects.create(product = product , quantity = 1 ,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart=cart,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        '''
        return HttpResponse(cart_item.quantity)
        exit()
        '''
        return redirect('cart')
def remove_cart(request,product_id,cart_item_id):
    #cart = Cart.objects.get(cart_id = cart_id(request))
    product = get_object_or_404(Product , id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user = request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request,product_id ,cart_item_id):
    product = get_object_or_404(Product , id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url = 'login')
def checkout(request , total = 0 , quantity = 0 , cart_items=None):

    try:
        tax=0
        grand_total=0
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
    return render(request,'store/checkout.html',context)
