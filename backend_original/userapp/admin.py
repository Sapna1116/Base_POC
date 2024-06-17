from django.contrib import admin
from .models import Comment

class CommentAdmin(admin.ModelAdmin):
    ordering = ('-id',)

admin.site.register(Comment, CommentAdmin)

from .models import Post

class PostAdmin(admin.ModelAdmin):
    ordering = ('-id',)

admin.site.register(Post, PostAdmin)

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'id', )
    ordering = ('id',)

admin.site.register(User, UserAdmin)