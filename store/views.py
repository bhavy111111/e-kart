from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.views import cart_id
from django.http import HttpResponse
from carts.models import CartItem
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q
from .models import Variation
# Create your views here.
def store(request , category_slug=None):
    categories = None
    products =None

    if category_slug !=None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories , is_available=True)
        #Pagination is also in category block also
        paginator = Paginator(products , 1)
        page = request.GET.get('page')
        page_obj  = paginator.get_page(page)
        prod_count = products.count()
    else:
        products  = Product.objects.all().filter(is_available=True)
        #Pagination Concept
        paginator = Paginator(products , 3)
        page = request.GET.get('page')
        page_obj  = paginator.get_page(page)
        prod_count = products.count()
    context={
        'products' : page_obj,
        'prod_count':prod_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug , product_slug):

    try:
        #Syntax , __slug as its category slug not store one
        #lookl_up type - __slug
        single_product = Product.objects.get(category__slug = category_slug , slug = product_slug)
        #colors = Variation.objects.filter(variation_category = 'color')
        #sizes = Variation.objects.filter(variation_category = 'size' )
        #IF product exist then it will return true(.exists()) otherweise false
        in_cart = CartItem.objects.filter(cart__cart_id = cart_id(request),product=single_product).exists()
        '''
        return HttpResponse(in_cart)
        exit()
        '''
    except Exception as e:
        raise e
    context={
    'single_product':single_product,
    'in_cart':in_cart,

    }

    return render(request , 'store/product_detail.html',context)
#Search Functionality at store page
def search(request):
    #keyword is basically the name of search button , check out navbar.html
    if 'keyword' in request.GET:
        #if keyword is present , suppose jeans , it will be store in keyword variable
        keyword = request.GET['keyword']
        if 'keyword':

            products = Product.objects.filter(Q(description__icontains=keyword)| Q(product_name__icontains=keyword))
            prod_count = products.count()
    context={
        'products':products,
        'prod_count':prod_count,
    }
    return render(request,'store/store.html',context)
