from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StyledFormMixin:
    """Adds the same CSS class to every input so the templates stay short."""

    def style_fields(self):
        for field in self.fields.values():
            if not isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault('class', 'input')


class RegisterForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT  # public registration is always a student
        if commit:
            user.save()
        return user


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'contact_number',
                  'course_year', 'bio', 'avatar')
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.style_fields()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        taken = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError('This email is already used by another account.')
        return email
