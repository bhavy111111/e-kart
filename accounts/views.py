from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegisterationForm,UserForm , UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages,auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order,OrderProduct
# Verfication send Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode ,  urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import cart_id
from carts.models import CartItem,Cart


def register(request):
    if request.method=='POST':
        form = RegisterationForm(request.POST)
        #Cleaned_Data -fetch values from form
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name = first_name,last_name=last_name,email=email,username=username,password=password)
            #Phone number is left
            user.phone_number  = phone_number
            user.save()

            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default\default-user.png'
            profile.save()

            # USER ACTIVATION LINK

            current_link = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_message.html',{
                'user':user,
                'domain':current_link,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            #SEND MAIL
            to_email = email
            send_email = EmailMessage(mail_subject , message , to=[to_email])
            send_email.send()
            #urlsafe_base_64_encode - is basically encoding primary key of the user
            #default_token_generator: is basically a method of gnerating token , it has two methods check token and make token
            messages.success(request,'Thank you for being our family , Email has been sent to your email address')
            return redirect('register')
    else:
        form = RegisterationForm()
    context = {
    'form':form,
    }
    return render(request , 'accounts/register.html',context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    empty_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        empty_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in empty_list:
                            index =empty_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')
#This decorator means that for logout first you have
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect ('login')

def activate(request , uidb64 , token):
    try:
        #Primary Key of the user will be given in uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError , ValueError , OverflowError , Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request , 'You account has been activated')
        return redirect ('login')
    else:
        messages.error(request,'Invalid Activation Link')
        return redirect('register')

@login_required(login_url = 'login')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id)
    print('Request',request.user.id)
    print(orders)
    orders_count = orders.count()
    print(orders_count)
    context = {
    'orders_count':orders_count,
    }
    return render(request , 'accounts/dashboard.html',context)

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_verification.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')

def reset_verification(request,token,uidb64):
    try:
        #Primary Key of the user will be given in uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError , ValueError , OverflowError , Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request , 'Please Reset Your Password')
        return redirect('reset_password')
    else:
        messages.error(request,'Invalid Reset Passowrd Activation Link')
        return redirect('login')

#@login_required(login_url = 'login')
def reset_password(request):
    if request.method=='POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid  = request.session.get('uid')
            user =  Account.objects.get(pk = uid)
            #set_password , save it into hash format , django inbuilt methods
            user.set_password(password)
            user.save()
            messages.success(request , 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request , 'Password donot match')
            return redirect('reset_password')
    else:
        return render(request , 'accounts/reset_password.html')

@login_required(login_url='login')
def my_orders(request):
    orders= Order.objects.filter(user=request.user , is_ordered=False).order_by('-created_at')
    context = {
    'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    print('hello',request.user)
    #return HttpResponse('Ok')
    user_all = UserProfile.objects.all()
    print('All User',user_all)
    userprofile = get_object_or_404(UserProfile ,user = request.user)
    print('UserProfile',userprofile)
    if request.method=='POST':
        #user_form = UserForm(request.POST , instance = request.user)
        user_form = UserForm(request.POST , instance = request.user)
        profile_form = UserProfileForm(request.POST ,request.FILES , instance = userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request , 'Your Profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance= userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile':userprofile
        }
    return render(request,'accounts/edit_profile.html',context)

def order_detail(request,order_id):
    #Lookup Method =  order is the table __order number way to extract
    order_detail  = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal+=i.product_price*i.price
    context={
    'order_detail':order_detail,
    'order':order,
    'sub_total':subtotal,
    }
    return render(request , 'accounts/order_detail.html',context)
