from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Task
        fields = ["project", "title", "description", "assignee", "status", "priority", "due_date"]