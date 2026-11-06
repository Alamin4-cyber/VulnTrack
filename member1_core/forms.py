import ipaddress
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Target, UserProfile


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(w, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            existing = w.attrs.get("class", "")
            w.attrs["class"] = f"{existing} {css}".strip()


class RegisterForm(BootstrapMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial="analyst")
    organization = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "organization")


class ProfileForm(BootstrapMixin, forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ("organization", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            u = self.instance.user
            self.fields["first_name"].initial = u.first_name
            self.fields["last_name"].initial = u.last_name
            self.fields["email"].initial = u.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            u = profile.user
            u.first_name = self.cleaned_data.get("first_name", "")
            u.last_name = self.cleaned_data.get("last_name", "")
            u.email = self.cleaned_data.get("email", "")
            u.save()
        return profile


class TargetForm(BootstrapMixin, forms.ModelForm):
    authorization_confirmed = forms.BooleanField(
        required=False, label="I confirm I am authorized to scan this target"
    )

    class Meta:
        model = Target
        fields = ("name", "domain", "description", "authorization_reference")

    def clean_domain(self):
        v = self.cleaned_data["domain"].strip().lower()
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        if not re.match(r"^([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$", v):
            raise forms.ValidationError("Enter a valid domain or IP.")
        return v

    def clean(self):
        c = super().clean()
        if c.get("authorization_confirmed") and not c.get("authorization_reference"):
            self.add_error("authorization_reference", "Provide an authorization reference.")
        return c