from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from .models import Anuncio, Comentario

class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('forum:login'))
        total_anuncios = Anuncio.objects.filter(usuario=request.user).count()
        return render(request, 'forum/perfil.html', {
            'request': request,
            'total_anuncios': total_anuncios,
        })


class EditProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('forum:login'))
        return render(request, 'forum/edit_profile.html', {'request': request})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('forum:login'))
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        errors = []
        if not username:
            errors.append('O nome de usuário é obrigatório.')
        elif username != request.user.username and User.objects.filter(username=username).exists():
            errors.append('Nome de usuário já em uso.')

        if errors:
            return render(request, 'forum/edit_profile.html', {
                'form_errors': errors,
                'username': username,
                'email': email,
                'request': request,
            })

        user = request.user
        user.username = username
        user.email = email
        user.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect(reverse('forum:perfil'))

class MainView(View):
    def get(self, request):
        anuncios = Anuncio.objects.order_by('-data_criacao')
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        q = request.GET.get('q', '').strip()
        try:
            if min_price:
                anuncios = anuncios.filter(preco__gte=Decimal(min_price))
            if max_price:
                anuncios = anuncios.filter(preco__lte=Decimal(max_price))
        except Exception:
            pass
        if q:
            anuncios = anuncios.filter(
                models.Q(titulo__icontains=q) | models.Q(descricao__icontains=q)
            )
        return render(request, 'forum/index.html', {
            'anuncios': anuncios,
            'min_price': min_price,
            'max_price': max_price,
            'q': q,
            'request': request,
        })

class AdDetailView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404('Anúncio inexistente')
        comentarios = ad.comentarios.order_by('-data_criacao')
        return render(request, 'forum/ad_detail.html', {
            'ad': ad,
            'request': request,
            'comentarios': comentarios,
        })

    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404('Anúncio inexistente')
        if request.user.is_authenticated:
            comentario_id = request.POST.get('comentario_id')
            resposta = request.POST.get('resposta', '').strip()
            if comentario_id and resposta and request.user == ad.usuario:
                try:
                    comentario = Comentario.objects.get(pk=comentario_id, anuncio=ad)
                    comentario.resposta_vendedor = resposta
                    comentario.save()
                except Comentario.DoesNotExist:
                    pass
            else:
                texto = request.POST.get('texto', '').strip()
                if texto:
                    Comentario.objects.create(anuncio=ad, autor=request.user, texto=texto)
        return redirect(reverse('forum:ad_detail', args=[ad.id]))

class CreateAdView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('forum:login')}?next={reverse('forum:ad_create')}")
        return render(request, 'forum/create_ad.html', {'request': request})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('forum:login')}?next={reverse('forum:ad_create')}")

        # basic validation
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        imagem_url = request.POST.get('imagem_url', '').strip() or None
        contato = request.POST.get('contato', '').strip() or None
        vendedor = request.user.username
        usuario = request.user

        errors = []
        if not titulo:
            errors.append('O título é obrigatório.')
        if not descricao:
            errors.append('A descrição é obrigatória.')

        try:
            preco = Decimal(request.POST.get('preco', '0').replace(',', '.'))
        except Exception:
            preco = Decimal('0')

        # enforce DecimalField limits (max_digits=10, decimal_places=2)
        MAX_PRECO = Decimal('99999999.99')
        if preco.copy_abs() > MAX_PRECO:
            errors.append('O preço excede o valor máximo permitido (99.999.999,99).')

        if errors:
            # render form again with errors and previous input
            context = {
                'form_errors': errors,
                'titulo': titulo,
                'descricao': descricao,
                'preco': request.POST.get('preco', ''),
                'imagem_url': request.POST.get('imagem_url', ''),
                'contato': request.POST.get('contato', ''),
                'request': request,
            }
            return render(request, 'forum/create_ad.html', context)

        # attempt save with exception handling to avoid site crash
        try:
            ad = Anuncio(titulo=titulo, descricao=descricao, preco=preco, imagem_url=imagem_url, vendedor=vendedor, usuario=usuario, contato=contato)
            ad.save()
        except Exception as exc:
            messages.error(request, 'Ocorreu um erro ao salvar o anúncio. Tente novamente.')
            # log to console for developer (visible in server logs)
            print('Error saving Ad:', exc)
            return redirect(reverse('forum:ad_create'))

        messages.success(request, f'Anúncio "{ad.titulo}" publicado com sucesso!')
        if request.POST.get('next') == 'novo':
            return redirect(reverse('forum:ad_create'))
        return redirect(reverse('forum:ad_detail', args=[ad.id]))

class SellerAdsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            vendedor = request.user.username
            anuncios = Anuncio.objects.filter(usuario=request.user).order_by('-data_criacao')
        else:
            vendedor = None
            anuncios = []
        return render(request, 'forum/seller_ads.html', {
            'anuncios': anuncios,
            'vendedor': vendedor,
            'request': request,
        })

class EditAdView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404('Anúncio inexistente')
        if not request.user.is_authenticated or request.user != ad.usuario:
            return redirect(reverse('forum:ad_detail', args=[ad_id]))
        return render(request, 'forum/edit_ad.html', {'ad': ad, 'request': request})

    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404('Anúncio inexistente')
        if not request.user.is_authenticated or request.user != ad.usuario:
            return redirect(reverse('forum:ad_detail', args=[ad_id]))
        ad.titulo = request.POST.get('titulo', ad.titulo).strip()
        ad.descricao = request.POST.get('descricao', ad.descricao).strip()
        ad.imagem_url = request.POST.get('imagem_url', '').strip() or None
        ad.vendedor = request.POST.get('vendedor', ad.vendedor).strip() or ad.vendedor
        ad.contato = request.POST.get('contato', '').strip() or None
        try:
            new_preco = Decimal(request.POST.get('preco', str(ad.preco)).replace(',', '.'))
            MAX_PRECO = Decimal('99999999.99')
            if new_preco.copy_abs() <= MAX_PRECO:
                ad.preco = new_preco
            else:
                messages.error(request, 'Preço excede o máximo permitido e não foi alterado.')
        except InvalidOperation:
            messages.error(request, 'Preço inválido. Mantendo valor anterior.')
        ad.save()
        messages.success(request, 'Anúncio atualizado com sucesso!')
        return redirect(reverse('forum:ad_detail', args=[ad.id]))

class DeleteAdView(View):
    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404('Anúncio inexistente')
        if not request.user.is_authenticated or request.user != ad.usuario:
            return redirect(reverse('forum:ad_detail', args=[ad_id]))
        ad.delete()
        messages.success(request, 'Anúncio excluído com sucesso.')
        return redirect(reverse('forum:index'))

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'forum/login.html', {'form': form, 'request': request})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            email_input = request.POST.get('email', '').strip()
            if not email_input:
                form.add_error(None, 'O e-mail é obrigatório.')
                return render(request, 'forum/login.html', {'form': form, 'request': request})
            # if the user has an email set, require it matches the provided email
            if user.email and email_input.lower() != (user.email or '').lower():
                form.add_error(None, 'E-mail não corresponde ao usuário.')
                return render(request, 'forum/login.html', {'form': form, 'request': request})
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or reverse('forum:index')
            return redirect(next_url)
        return render(request, 'forum/login.html', {'form': form, 'request': request})

class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'forum/register.html', {'form': form, 'request': request})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or reverse('forum:index')
            return redirect(next_url)
        return render(request, 'forum/register.html', {'form': form, 'request': request})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('forum:index'))
