from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Punishment
from .forms import PunishmentForm, UnbanForm
from servers.models import Server
from admins.models import Admin


@login_required
def punishments_list(request):
    punishments = Punishment.objects.all().select_related('admin', 'server', 'unbanned_by')

    punishment_type_filter = request.GET.get('type')
    server_filter = request.GET.get('server')
    status_filter = request.GET.get('status')

    if punishment_type_filter:
        punishments = punishments.filter(punishment_type=punishment_type_filter)

    if server_filter:
        punishments = punishments.filter(server_id=server_filter)

    if status_filter == 'active':
        punishments = punishments.filter(is_active=True)
    elif status_filter == 'inactive':
        punishments = punishments.filter(is_active=False)

    servers = Server.objects.all().order_by('name')

    context = {
        'punishments': punishments,
        'servers': servers,
        'selected_type': punishment_type_filter,
        'selected_server': server_filter,
        'selected_status': status_filter,
    }
    return render(request, 'punishments/list.html', context)


@login_required
def punishment_add(request):
    if request.method == 'POST':
        form = PunishmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('punishments:list')
    else:
        form = PunishmentForm()
    return render(request, 'punishments/form.html', {'form': form, 'action': 'Добавить'})


@login_required
def punishment_edit(request, pk):
    punishment = get_object_or_404(Punishment, pk=pk)
    if request.method == 'POST':
        form = PunishmentForm(request.POST, instance=punishment)
        if form.is_valid():
            form.save()
            return redirect('punishments:list')
    else:
        form = PunishmentForm(instance=punishment)
    return render(request, 'punishments/form.html', {'form': form, 'action': 'Редактировать'})


@login_required
def punishment_delete(request, pk):
    punishment = get_object_or_404(Punishment, pk=pk)
    if request.method == 'POST':
        punishment.delete()
        return redirect('punishments:list')
    return render(request, 'punishments/delete.html', {'punishment': punishment})


@login_required
def punishment_unban(request, pk):
    punishment = get_object_or_404(Punishment, pk=pk)

    if not punishment.is_active:
        return redirect('punishments:list')

    if request.method == 'POST':
        form = UnbanForm(request.POST)
        if form.is_valid():
            punishment.is_active = False
            punishment.unban_reason = form.cleaned_data['unban_reason'] or 'Снято администратором'
            # TODO: установить unbanned_by из текущего пользователя
            punishment.save()
            return redirect('punishments:list')
    else:
        form = UnbanForm()

    return render(request, 'punishments/unban.html', {'punishment': punishment, 'form': form})
