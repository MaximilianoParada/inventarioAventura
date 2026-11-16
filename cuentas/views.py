from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, StaffUserCreationForm, StaffUserUpdateForm
from .models import Role, User
from .permissions import role_required

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'cuentas/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return redirect('login')
    return redirect('dashboard')


@role_required(Role.ADMINISTRATOR)
def user_list_view(request):
    users = User.objects.prefetch_related('userrole_set__role').order_by('username')
    return render(request, 'cuentas/user_list.html', {'users': users})


@role_required(Role.ADMINISTRATOR)
def user_create_view(request):
    form = StaffUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('user_list')
    return render(request, 'cuentas/user_form.html', {'form': form, 'title': 'Crear usuario'})


@role_required(Role.ADMINISTRATOR)
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = StaffUserUpdateForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('user_list')
    return render(
        request,
        'cuentas/user_form.html',
        {'form': form, 'title': f'Editar usuario: {user.username}', 'account': user},
    )