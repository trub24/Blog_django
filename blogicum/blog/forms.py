from django import forms
from django.utils import timezone
from blog.models import Post, Comment, User


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()
        ).strftime('%Y-%m-%dT%H:%M')

    class Meta:
        model = Post
        fields = ('title', 'text', 'image',
                  'location', 'category', 'pub_date',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            )
        }


class CommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
