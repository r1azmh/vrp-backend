from django import forms as django_forms


class LoginForm(django_forms.Form):
    username = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
        })
    )
    password = django_forms.CharField(
        widget=django_forms.PasswordInput(attrs={
            "placeholder": "Password",
            "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
        })
    )


class SignupForm(django_forms.Form):
    username = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
        })
    )
    password = django_forms.CharField(
        widget=django_forms.PasswordInput(attrs={
            "placeholder": "Password",
            "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
        })
    )
    confirm_password = django_forms.CharField(
            widget=django_forms.PasswordInput(attrs={
                "placeholder": "Password",
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            })
        )

