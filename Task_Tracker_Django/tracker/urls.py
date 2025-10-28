from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskUpdateView, TaskDetailView, TaskDeleteView,
    ProjectListCreateView, project_create
)

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/new/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),

    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/new/", project_create, name="project-create"),
]