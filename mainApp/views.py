from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .models import *
def home(Request):
    data = Product.objects.all().order_by('id').reverse()[:8] 
    return render(Request,"index.html",{'data':data})

def shop(Request,mc,sc,br):
    if(mc=='All' and sc=='All' and br=='All'):
        data = Product.objects.all().order_by('id').reverse()
    elif(mc!='All' and sc=='All' and br=='All'):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc)).order_by('id').reverse()
    elif(mc=='All' and sc!='All' and br=='All'):
        data = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    elif(mc=='All' and sc=='All' and br!='All'):
        data = Product.objects.filter(brand=Brand.objects.get(name=br)).order_by('id').reverse()
    elif(mc!='All' and sc!='All' and br=='All'):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    elif(mc!='All' and sc=='All' and br!='All'):
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br)).order_by('id').reverse()
    elif(mc=='All' and sc!='All' and br!='All'):
        data = Product.objects.filter(brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    else:
        data = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc)).order_by('id').reverse()
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    return render(Request,"shop.html",{'data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':mc,'sc':sc,'br':br})

def singleProduct(Request,id):
    data = Product.objects.get(id=id)
    return render(Request,"single-product.html",{'data':data})

def loginPage(Request):
    if(Request.method=="POST"):
        username = Request.POST.get("username")
        password = Request.POST.get("password")
        user = authenticate(username=username,password=password)
        if(user is not None):
            login(Request,user)
            if(user.is_superuser):
                return redirect("/admin")
            else:
                return redirect("/profile")
        else:        
           messages.error(Request,"Invalid Username or Password!!!!")
    return render(Request,"login.html")

def logoutPage(Request):
    logout(Request)
    return redirect("/login")

def signupPage(Request):
    if(Request.method=="POST"):
        p = Request.POST.get("password")
        cp = Request.POST.get("cpassword")
        if(p==cp):
            b = Buyer()
            b.name = Request.POST.get("name")
            b.username = Request.POST.get("username")
            b.phone = Request.POST.get("phone")
            b.email = Request.POST.get("email")
            user = User(username=b.username,email=b.email,password=p)
            if(user):
                user.save()
                b.save()
                return redirect("/login/")
            else:
                messages.error(Request,"Username Already Taken!!!!!!")                
        else:
            messages.error(Request,"Password And Confirm Password Doesn't Matched!!!")
    return render(Request,"signup.html")


@login_required(login_url='/login/')
def profilePage(Request):
    user = User.objects.get(username=Request.user)
    if(user.is_superuser):
        return redirect("/admin")
    else:
        buyer = Buyer.objects.get(username=user.username)
        wishlist = Wishlist.objects.filter(user=buyer)
    return render(Request,"profile.html",{'user':buyer,'wishlist':wishlist})


@login_required(login_url='/login/')
def updateProfilePage(Request):
    user = User.objects.get(username=Request.user)
    if(user.is_superuser):
        return redirect("/admin")
    else:
        buyer = Buyer.objects.get(username=user.username)
        if(Request.method=="POST"):
            buyer.name = Request.POST.get("name")
            buyer.email = Request.POST.get("email")
            buyer.phone = Request.POST.get("phone")
            buyer.addressline1 = Request.POST.get("addressline1")
            buyer.addressline2 = Request.POST.get("addressline2")
            buyer.addressline3 = Request.POST.get("addressline3")
            buyer.pin = Request.POST.get("pin")
            buyer.city = Request.POST.get("city")
            buyer.state = Request.POST.get("state")
            if(Request.FILES.get("pic")!=""):
                buyer.pic = Request.FILES.get("pic")
            buyer.save()
            return redirect("/profile")
    return render(Request,"update-profile.html",{'user':buyer})

@login_required(login_url='/login/')
def addToCart(Request,id):
    # Request.session.flush()
    cart = Request.session.get('cart',None)
    p = Product.objects.get(id=id)
    if(cart is None):
        cart = {str(p.id):{'pid':p.id,'pic':p.pic1.url,'name':p.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':1,'total':p.finalprice,'maincategory':p.maincategory.name,'subcategory':p.subcategory.name,'brand':p.brand.name}}
    else:
        if(str(p.id) in cart):
            item = cart[str(p.id)]
            item['qty']=item['qty']+1
            item['total']=item['total']+item['price']
            cart[str(p.id)]=item
        else:
            cart.setdefault(str(p.id),{'pid':p.id,'pic':p.pic1.url,'name':p.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':1,'total':p.finalprice,'maincategory':p.maincategory.name,'subcategory':p.subcategory.name,'brand':p.brand.name})           

    Request.session['cart']=cart
    Request.session.set_expiry(60*60*24*45)
    return redirect("/cart")

@login_required(login_url='/login/')
def cartPage(Request):
    cart = Request.session.get('cart',None)
    c = []
    total = 0
    shipping = 0
    if(cart is not None):
        for value in cart.values():
            total = total + value['total']
            c.append(value)
        if(total<1000 and total>0):
            shipping = 150
    final = total+shipping
    return render(Request,"cart.html",{'cart':c,'total':total,'shipping':shipping,'final':final})

@login_required(login_url='/login/')
def deleteCart(Request,pid):
    cart = Request.session.get('cart',None)
    if(cart):
        for key in cart.keys():
            if(str(pid)==key):
                del cart[key]
                break
        Request.session['cart']=cart
    return redirect("/cart")

@login_required(login_url='/login/')
def updateCart(Request,pid,op):
    cart = Request.session.get('cart',None)
    if(cart):
        for key,value in cart.items():
            if(str(pid)==key):
                if(op=="inc"):
                    value['qty']=value['qty']+1
                    value['total']=value['total']+value['price']
                elif(op=='dec' and value['qty']>1):
                    value['qty']=value['qty']-1
                    value['total']=value['total']-value['price']
                cart[key] = value
                break
        Request.session['cart']=cart
    return redirect("/cart")

@login_required(login_url='/login/')
def addToWishlist(Request,pid):
    try:
        user = Buyer.objects.get(username=Request.user.username)
        p = Product.objects.get(id=pid)
        try:
            w = Wishlist.objects.get(user=user,product=p)
        except:
            w = Wishlist()
            w.user = user
            w.product = p
            w.save()
        return redirect("/profile") 
    except:
        return redirect("/admin")

@login_required(login_url='/login/')
def deleteWishlist(Request,pid):
    try:
        user = Buyer.objects.get(username=Request.user.username)
        p = Product.objects.get(id=pid)
        try:
            w = Wishlist.objects.get(user=user,product=p)
            w.delete()
        except:
            pass
    except:
        pass
    return redirect("/profile")