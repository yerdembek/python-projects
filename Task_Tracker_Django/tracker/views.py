from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from .models import Task, Project
from .forms import TaskForm, ProjectForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    paginate_by = 15

    def get_queryset(self):
        qs = (
            Task.objects
            .select_related("project", "assignee")
            .filter(Q(project__owner=self.request.user) | Q(assignee=self.request.user))
        )
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        project = self.request.GET.get("project")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if project:
            qs = qs.filter(project_id=project)
        return qs

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tracker/task_form.html"
    success_url = reverse_lazy("task-list")

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tracker/task_form.html"
    success_url = reverse_lazy("task-list")

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tracker/task_detail.html"

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tracker/task_confirm_delete.html"
    success_url = reverse_lazy("task-list")

class ProjectListCreateView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "tracker/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("project-list")
    else:
        form = ProjectForm()
    return render(request, "tracker/project_form.html", {"form": form})