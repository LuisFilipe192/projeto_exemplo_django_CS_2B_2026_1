from django.urls import path
from . import views

app_name = 'forum'
urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('ad/<int:ad_id>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ad/inserir/', views.CreateAdView.as_view(), name='ad_create'),
    path('meus-anuncios/', views.SellerAdsView.as_view(), name='seller_ads'),
    path('ad/<int:ad_id>/editar/', views.EditAdView.as_view(), name='ad_edit'),
    path('ad/<int:ad_id>/excluir/', views.DeleteAdView.as_view(), name='ad_delete'),
    path('perfil/', views.ProfileView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditProfileView.as_view(), name='edit_profile'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('cadastro/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
