from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User



# class LoginForm(AuthenticationForm):
#     username = forms.CharField(label="Username or Matric No")
#     password = forms.CharField(widget=forms.PasswordInput)



class StyledFormMixin:
    """Mixin to add Bootstrap styles to all fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.label


class SignupForm(StyledFormMixin, UserCreationForm):
    role = forms.ChoiceField(choices=[('Admin', 'Admin'), 
                    ('Student', 'Student'),
                    ("Lecturer", "Lecturer")
                    ], required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role','matric_no', 'password1', 'password2']
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        matric_no = cleaned_data.get("matric_no")

        if role == "Student" and not matric_no:
            self.add_error("matric_no", "Matric number is required for students.")

        # If role is NOT Student, force matric_no to None
        if role != "Student":
            cleaned_data["matric_no"] = None

        return cleaned_data


class LoginForm(StyledFormMixin,AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class CustomLoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.label
