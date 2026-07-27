from django import forms
from .models import Provider, ProviderPhoto

class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['full_name', 'category', 'phone', 'email', 'address',
                  'country', 'city', 'description', 'tags']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван Иванов'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Категория'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ул. Ленина, д. 10'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Россия'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Москва'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание услуг...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'тег1, тег2, тег3'}),
        }

class ProviderPhotoForm(forms.ModelForm):
    class Meta:
        model = ProviderPhoto
        fields = ['image', 'caption', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Подпись к фото'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }