from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import SkillPost
from .forms import SkillPostForm

# READ: List all skills
class SkillListView(LoginRequiredMixin, ListView):
    model = SkillPost
    template_name = 'skills/skill_list.html'
    context_object_name = 'skills'
    ordering = ['-created_at']

# CREATE: Add a new skill
class SkillCreateView(LoginRequiredMixin, CreateView):
    model = SkillPost
    form_class = SkillPostForm
    template_name = 'skills/skill_form.html'
    success_url = reverse_lazy('skill-list')

    def form_valid(self, form):
        form.instance.user = self.request.user 
        return super().form_valid(form)

# UPDATE: Edit an existing skill
class SkillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SkillPost
    form_class = SkillPostForm
    template_name = 'skills/skill_form.html'
    success_url = reverse_lazy('skill-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user

# DELETE: Remove a skill
class SkillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SkillPost
    template_name = 'skills/skill_confirm_delete.html'
    success_url = reverse_lazy('skill-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user