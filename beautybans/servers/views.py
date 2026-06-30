from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Server
from .forms import ServerForm

@login_required
def servers_list(request):
    servers = Server.objects.all().order_by('-created_at')
    return render(request, 'servers/list.html', {'servers': servers})

@login_required
def server_add(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('servers:list')
    else:
        form = ServerForm()
    return render(request, 'servers/form.html', {'form': form, 'action': 'Добавить'})

@login_required
def server_edit(request, pk):
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            return redirect('servers:list')
    else:
        form = ServerForm(instance=server)
    return render(request, 'servers/form.html', {'form': form, 'action': 'Редактировать'})

@login_required
def server_delete(request, pk):
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        server.delete()
        return redirect('servers:list')
    return render(request, 'servers/delete.html', {'server': server})
