from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import View
from .models import Anuncio


class MainView(View):
    def get(self, request):
        anuncios = Anuncio.objects.order_by("-data_criacao")
        q         = request.GET.get('q', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        try:
            if q:
                anuncios = anuncios.filter(titulo__icontains=q)
            if min_price:
                anuncios = anuncios.filter(preco__gte=min_price)
            if max_price:
                anuncios = anuncios.filter(preco__lte=max_price)
        except Exception:
            pass
        contexto = {
            'anuncios': anuncios,
            'q': q,
            'min_price': min_price,
            'max_price': max_price,
        }
        return render(request, 'forum/index.html', contexto)


class AdDetailView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        return render(request, 'forum/ad_detail.html', {'ad': ad})


class CreateAdView(View):
    def get(self, request):
        return render(request, 'forum/create_ad.html')

    def post(self, request):
        titulo     = request.POST.get('titulo', '').strip()
        descricao  = request.POST.get('descricao', '').strip()
        preco      = request.POST.get('preco') or 0
        imagem_url = request.POST.get('imagem_url', '').strip()

        if request.user.is_authenticated:
            vendedor = request.user.username
        else:
            vendedor = request.POST.get('vendedor', '').strip() or 'anônimo'

        if not titulo:
            return render(request, 'forum/create_ad.html', {'erro': 'O título é obrigatório.'})

        ad = Anuncio(titulo=titulo, descricao=descricao, preco=preco,
                     imagem_url=imagem_url, vendedor=vendedor)
        ad.save()

        if request.POST.get('next') == 'novo':
            return redirect(reverse('forum:ad_create'))
        return redirect(reverse('forum:ad_detail', args=[ad.id]))


class SellerAdsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            vendedor = request.user.username
            anuncios = Anuncio.objects.filter(vendedor=vendedor).order_by('-data_criacao')
        else:
            vendedor = None
            anuncios = []
        return render(request, 'forum/seller_ads.html', {'anuncios': anuncios, 'vendedor': vendedor})


class EditAdView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        return render(request, 'forum/edit_ad.html', {'ad': ad})

    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        titulo = request.POST.get('titulo', '').strip()
        if not titulo:
            return render(request, 'forum/edit_ad.html', {'ad': ad, 'erro': 'O título é obrigatório.'})
        ad.titulo     = titulo
        ad.descricao  = request.POST.get('descricao', '').strip()
        ad.preco      = request.POST.get('preco') or ad.preco
        ad.imagem_url = request.POST.get('imagem_url', '').strip()
        ad.save()
        return redirect(reverse('forum:ad_detail', args=[ad.id]))


class DeleteAdView(View):
    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        ad.delete()
        return redirect(reverse('forum:index'))
