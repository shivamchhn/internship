from django.contrib import admin
from home.models import Post, Comment, LikeDislike


admin.site.register(Post)

admin.site.register(Comment)
admin.site.register(LikeDislike)
