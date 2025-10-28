from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "description", "owner__username")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assignee", "status", "priority", "due_date", "updated_at")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description", "assignee__username")