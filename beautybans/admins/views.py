from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Admin, AdminGroup, AdminServer
from .forms import AdminForm, AdminGroupForm, AdminServerForm
from servers.models import Server


@login_required
def admin_panel(request):
    admins = Admin.objects.all().order_by('-created_at')
    groups = AdminGroup.objects.all().order_by('name')
    permissions = AdminServer.objects.all().select_related('admin', 'server', 'group').order_by('-created_at')

    server_filter = request.GET.get('server')
    group_filter = request.GET.get('group')

    if server_filter:
        permissions = permissions.filter(server_id=server_filter)

    if group_filter:
        permissions = permissions.filter(group_id=group_filter)

    servers = Server.objects.all().order_by('name')
    all_groups = AdminGroup.objects.all().order_by('name')

    context = {
        'admins': admins,
        'groups': groups,
        'permissions': permissions,
        'servers': servers,
        'all_groups': all_groups,
        'selected_server': server_filter,
        'selected_group': group_filter,
    }
    return render(request, 'admins/admin_panel.html', context)


@login_required
def admins_list(request):
    admins = Admin.objects.all().order_by('-created_at')
    return render(request, 'admins/admins_list.html', {'admins': admins})


@login_required
def admin_add(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admins:admin_panel')
    else:
        form = AdminForm()
    return render(request, 'admins/admin_form.html', {'form': form, 'action': 'Добавить'})


@login_required
def admin_edit(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            return redirect('admins:admin_panel')
    else:
        form = AdminForm(instance=admin)
    return render(request, 'admins/admin_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
def admin_delete(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == 'POST':
        admin.delete()
        return redirect('admins:admin_panel')
    return render(request, 'admins/admin_delete.html', {'admin': admin})


@login_required
def groups_list(request):
    groups = AdminGroup.objects.all().order_by('name')
    return render(request, 'admins/groups_list.html', {'groups': groups})


@login_required
def group_add(request):
    if request.method == 'POST':
        form = AdminGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('admins:admin_panel') + '?tab=groups')
    else:
        form = AdminGroupForm()
    return render(request, 'admins/group_form.html', {'form': form, 'action': 'Добавить'})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(AdminGroup, pk=pk)
    if request.method == 'POST':
        form = AdminGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect(reverse('admins:admin_panel') + '?tab=groups')
    else:
        form = AdminGroupForm(instance=group)
    return render(request, 'admins/group_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
def group_delete(request, pk):
    group = get_object_or_404(AdminGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect(reverse('admins:admin_panel') + '?tab=groups')
    return render(request, 'admins/group_delete.html', {'group': group})


@login_required
def permissions_list(request):
    from servers.models import Server

    permissions = AdminServer.objects.all().select_related('admin', 'server', 'group').order_by('-created_at')

    server_filter = request.GET.get('server')
    group_filter = request.GET.get('group')

    if server_filter:
        permissions = permissions.filter(server_id=server_filter)

    if group_filter:
        permissions = permissions.filter(group_id=group_filter)

    servers = Server.objects.all().order_by('name')
    groups = AdminGroup.objects.all().order_by('name')

    context = {
        'permissions': permissions,
        'servers': servers,
        'groups': groups,
        'selected_server': server_filter,
        'selected_group': group_filter,
    }
    return render(request, 'admins/permissions_list.html', context)


@login_required
def permission_add(request):
    import json

    if request.method == 'POST':
        form = AdminServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('admins:admin_panel') + '?tab=permissions')
    else:
        form = AdminServerForm()

    groups_data = {g.id: {'flags': g.flags, 'immunity': g.immunity} for g in AdminGroup.objects.all()}

    return render(request, 'admins/permission_form.html', {
        'form': form,
        'action': 'Добавить',
        'groups_data_json': json.dumps(groups_data)
    })


@login_required
def permission_edit(request, pk):
    import json

    permission = get_object_or_404(AdminServer, pk=pk)
    if request.method == 'POST':
        form = AdminServerForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            return redirect(reverse('admins:admin_panel') + '?tab=permissions')
    else:
        form = AdminServerForm(instance=permission)

    groups_data = {g.id: {'flags': g.flags, 'immunity': g.immunity} for g in AdminGroup.objects.all()}

    return render(request, 'admins/permission_form.html', {
        'form': form,
        'action': 'Редактировать',
        'groups_data_json': json.dumps(groups_data)
    })


@login_required
def permission_delete(request, pk):
    permission = get_object_or_404(AdminServer, pk=pk)
    if request.method == 'POST':
        permission.delete()
        return redirect(reverse('admins:admin_panel') + '?tab=permissions')
    return render(request, 'admins/permission_delete.html', {'permission': permission})
