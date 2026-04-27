from django.urls import path
from . import views

app_name = 'forum'
urlpatterns = [
    # ex: /forum/
    path("", views.MainView.as_view(), name="index"),
    path("ad/<int:ad_id>/", views.AdDetailView.as_view(), name="ad_detail"),
    path("ad/inserir/", views.CreateAdView.as_view(), name="ad_create"),
    path("meus-anuncios/", views.SellerAdsView.as_view(), name="seller_ads"),
    path("ad/<int:ad_id>/editar/", views.EditAdView.as_view(), name="ad_edit"),
    path("ad/<int:ad_id>/excluir/", views.DeleteAdView.as_view(), name="ad_delete"),
    
    
]