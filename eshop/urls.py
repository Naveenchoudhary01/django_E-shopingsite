from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mainApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('shop/<str:mc>/<str:sc>/<str:br>/',views.shop),
    path('single-product/<int:id>/',views.singleProduct),
    path('login/',views.loginPage),
    path('logout/',views.logoutPage),
    path('signup/',views.signupPage),
    path('profile/',views.profilePage),
    path('update-profile/',views.updateProfilePage),
    path('add-to-cart/<int:id>/',views.addToCart),
    path('cart/',views.cartPage),
    path('delete-cart/<int:pid>/',views.deleteCart),
    path('update-cart/<int:pid>/<str:op>/',views.updateCart),
    path('add-to-wishlist/<int:pid>/',views.addToWishlist),
    path('delete-wishlist/<int:pid>/',views.deleteWishlist),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
