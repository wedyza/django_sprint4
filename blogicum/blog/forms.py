from pytils.translit import slugify

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания или обновления поста."""
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'pub_date', 'location', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea()
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
