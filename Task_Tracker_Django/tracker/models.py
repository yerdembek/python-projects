from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "doing", "In Progress"
        DONE = "done", "Done"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.TODO)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "due_date", "title"]

    def __str__(self):
        return self.title