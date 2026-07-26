from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import User
from providers.models import Provider
from reviews.models import Review
from chat.models import Chat, Message
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def index(request):
    countries = Provider.objects.values_list('country', flat=True).distinct()
    countries = [c for c in countries if c]
    categories = Provider.objects.values_list('category', flat=True).distinct()
    categories = list(set(list(categories) + settings.CATEGORIES))
    categories.sort()
    return render(request, 'index.html', {'countries': countries, 'categories': categories})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                user.last_login = timezone.now()
                user.save()
                messages.success(request, 'Вы успешно вошли!')
                return redirect(request.GET.get('next', 'index'))
            else:
                messages.error(request, 'Ваш аккаунт заблокирован')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html')

        if len(password1) < 6:
            messages.error(request, 'Пароль должен содержать минимум 6 символов')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Имя пользователя уже занято')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже зарегистрирован')
            return render(request, 'register.html')

        user = User(
            username=username,
            email=email,
            phone=phone
        )
        user.set_password(password1)
        user.save()

        messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
        return redirect('login')

    return render(request, 'register.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
def profile(request):
    stats = {
        'reviews_count': Review.objects.filter(user=request.user).count(),
        'approved_reviews': Review.objects.filter(user=request.user, is_approved=True).count(),
        'pending_reviews': Review.objects.filter(user=request.user, is_approved=False).count(),
        'messages_count': Message.objects.filter(sender=request.user).count(),
        'unread_count': request.user.get_unread_count()
    }
    return render(request, 'profile.html', {'user': request.user, 'stats': stats})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


def search_providers(request):
    country = request.GET.get('country', '')
    category = request.GET.get('category', '')
    query = request.GET.get('query', '')

    providers = Provider.objects.filter(is_active=True)

    if country:
        providers = providers.filter(country=country)

    if category:
        providers = providers.filter(category=category)

    if query:
        providers = providers.filter(
            Q(full_name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query) |
            Q(address__icontains=query) |
            Q(tags__icontains=query)
        )

    providers = providers.order_by('-rating')
    data = [{
        'id': p.id,
        'full_name': p.full_name,
        'category': p.category,
        'phone': p.phone,
        'email': p.email,
        'address': p.address,
        'country': p.country,
        'city': p.city,
        'rating': p.rating,
        'description': p.description,
        'tags': p.tags,
        'tags_list': p.get_tags_list(),
        'is_verified': p.is_verified,
        'is_active': p.is_active,
        'created_by': p.created_by_id
    } for p in providers]

    return JsonResponse(data, safe=False)


@login_required
def add_provider(request):
    if request.method == 'POST':
        provider = Provider(
            full_name=request.POST.get('full_name'),
            category=request.POST.get('category'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            country=request.POST.get('country'),
            city=request.POST.get('city'),
            description=request.POST.get('description'),
            tags=request.POST.get('tags'),
            created_by=request.user
        )
        provider.save()
        messages.success(request, 'Специалист добавлен!')
        return redirect('index')

    return render(request, 'add_provider.html', {'categories': settings.CATEGORIES})


def provider_detail(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)
    if not provider.is_active:
        messages.warning(request, 'Этот специалист временно недоступен')
    return render(request, 'provider_detail.html', {'provider': provider})


@login_required
def add_review(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)

    if not provider.is_active:
        messages.error(request, 'Этот специалист временно недоступен')
        return redirect('provider_detail', provider_id=provider.id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')

        if rating < 1 or rating > 5:
            messages.error(request, 'Пожалуйста, выберите оценку от 1 до 5')
            return redirect('provider_detail', provider_id=provider.id)

        existing_review = Review.objects.filter(provider=provider, user=request.user).first()
        if existing_review:
            messages.warning(request, 'Вы уже оставляли отзыв на этого специалиста')
            return redirect('provider_detail', provider_id=provider.id)

        review = Review(
            provider=provider,
            user=request.user,
            rating=rating,
            comment=comment
        )
        review.save()
        provider.calculate_rating()
        messages.success(request, 'Спасибо за отзыв! Он будет опубликован после модерации.')

    return redirect('provider_detail', provider_id=provider.id)