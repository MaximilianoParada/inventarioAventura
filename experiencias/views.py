from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from cuentas.models import Role
from cuentas.permissions import is_administrator, role_required

from .forms import CategoryForm, ExperienceForm
from .models import Category, Experience, Reservation


def catalog_view(request):
    experiences = (
        Experience.objects.filter(
            is_active=True,
            category__is_active=True,
            scheduled_at__gte=timezone.now(),
        )
        .select_related('category', 'creator')
        .annotate(reservation_count=Count('reservations'))
    )
    return render(request, 'experiencias/catalog.html', {'experiences': experiences})


@role_required(Role.ADMINISTRATOR, Role.GUIDE_OPERATOR)
def experience_list_view(request):
    experiences = Experience.objects.select_related('category', 'creator').annotate(
        reservation_count=Count('reservations')
    )
    if not is_administrator(request.user):
        experiences = experiences.filter(creator=request.user)
    return render(request, 'experiencias/experience_list.html', {'experiences': experiences})


@role_required(Role.ADMINISTRATOR, Role.GUIDE_OPERATOR)
def experience_create_view(request):
    form = ExperienceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        experience = form.save(commit=False)
        experience.creator = request.user
        experience.full_clean()
        experience.save()
        messages.success(request, 'Experiencia creada correctamente.')
        return redirect('experience_list')
    return render(
        request,
        'experiencias/experience_form.html',
        {'form': form, 'title': 'Crear experiencia'},
    )


@role_required(Role.ADMINISTRATOR, Role.GUIDE_OPERATOR)
def experience_update_view(request, pk):
    experiences = Experience.objects.select_related('category', 'creator')
    if not is_administrator(request.user):
        experiences = experiences.filter(creator=request.user)
    experience = get_object_or_404(experiences, pk=pk)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == 'POST' and form.is_valid():
        updated_experience = form.save(commit=False)
        updated_experience.full_clean()
        updated_experience.save()
        messages.success(request, 'Experiencia actualizada correctamente.')
        return redirect('experience_list')
    return render(
        request,
        'experiencias/experience_form.html',
        {'form': form, 'title': 'Editar experiencia', 'experience': experience},
    )


@role_required(Role.ADMINISTRATOR)
def experience_delete_view(request, pk):
    experience = get_object_or_404(Experience, pk=pk)
    if request.method == 'POST':
        title = experience.title
        experience.delete()
        messages.success(request, f'La experiencia «{title}» y sus reservas fueron eliminadas.')
        return redirect('experience_list')
    return render(
        request,
        'experiencias/confirm_delete.html',
        {
            'object': experience,
            'cancel_url': 'experience_list',
            'has_reservations': experience.reservations.exists(),
        },
    )


@role_required(Role.ADMINISTRATOR)
def category_list_view(request):
    categories = Category.objects.annotate(experience_count=Count('experiences'))
    return render(request, 'experiencias/category_list.html', {'categories': categories})


@role_required(Role.ADMINISTRATOR)
def category_create_view(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada correctamente.')
        return redirect('category_list')
    return render(
        request,
        'experiencias/category_form.html',
        {'form': form, 'title': 'Crear categoría'},
    )


@role_required(Role.ADMINISTRATOR)
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('category_list')
    return render(
        request,
        'experiencias/category_form.html',
        {'form': form, 'title': 'Editar categoría', 'category': category},
    )


@role_required(Role.ADMINISTRATOR)
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.delete()
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar una categoría con experiencias asociadas. Desactívala en su lugar.',
            )
        else:
            messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('category_list')
    return render(
        request,
        'experiencias/confirm_delete.html',
        {'object': category, 'cancel_url': 'category_list'},
    )


@role_required(Role.TOURIST_CLIENT)
@require_POST
def reservation_create_view(request, pk):
    try:
        with transaction.atomic():
            experience = get_object_or_404(
                Experience.objects.select_for_update().filter(
                    is_active=True,
                    category__is_active=True,
                    scheduled_at__gte=timezone.now(),
                ),
                pk=pk,
            )
            if Reservation.objects.filter(user=request.user, experience=experience).exists():
                messages.warning(request, 'Ya tienes una inscripción para esta experiencia.')
                return redirect('catalog')
            if experience.reservations.count() >= experience.capacity:
                messages.error(request, 'La experiencia ya no tiene cupos disponibles.')
                return redirect('catalog')
            Reservation.objects.create(user=request.user, experience=experience)
    except IntegrityError:
        messages.warning(request, 'Ya tienes una inscripción para esta experiencia.')
    else:
        messages.success(request, 'Tu inscripción quedó registrada como pendiente de pago.')
    return redirect('reservation_list')


@role_required(Role.ADMINISTRATOR, Role.TOURIST_CLIENT)
def reservation_list_view(request):
    reservations = Reservation.objects.select_related('user', 'experience', 'experience__category')
    if not is_administrator(request.user):
        reservations = reservations.filter(user=request.user)
    return render(request, 'experiencias/reservation_list.html', {'reservations': reservations})


@role_required(Role.ADMINISTRATOR)
@require_POST
def reservation_status_update_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    status = request.POST.get('payment_status')
    if status not in dict(Reservation.PAYMENT_CHOICES):
        messages.error(request, 'El estado de pago seleccionado no es válido.')
    else:
        reservation.payment_status = status
        reservation.save(update_fields=['payment_status'])
        messages.success(request, 'Estado de pago actualizado.')
    return redirect('reservation_list')
