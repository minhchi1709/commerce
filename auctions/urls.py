from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path('listings/<int:listing_id>', views.listing, name='listing'),
    path('listings/bid/<int:listing_id>', views.bid, name='bid'),
    path('add_to_watchlist/<int:listing_id>', views.add_to_watchlist, name='add_to_watchlist'),
    path('show_watchlist', views.show_watchlist, name='show_watchlist'),
    path('category', views.category, name='category'),
    path('<int:listing_id>/add_comment', views.add_comment, name='add_comment'),
    path('own_listings', views.own_listings, name='own_listings'),
    path('edit/<int:listing_id>', views.edit, name='edit_listing'),
    path('close/<int:listing_id>', views.close, name='close_listing'),
]
