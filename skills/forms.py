from django import forms
from .models import SkillPost

class SkillPostForm(forms.ModelForm):
    class Meta:
        model = SkillPost
        fields = ['title', 'description', 'skill_type']