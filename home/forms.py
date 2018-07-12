from django import forms
from home.models import Post, Comment


class HomeForm(forms.ModelForm):
    picture = forms.ImageField()
    post = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder':'write your post..'
        }

    ))

    class Meta:
        model = Post
        fields = ('picture', 'post')


class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder':'write your comment...'
        }
    ))

    class Meta:
        model = Comment
        fields = ('comment',)