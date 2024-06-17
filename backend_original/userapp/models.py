from django.db import models
from django.contrib.auth.models import AbstractUser

def user_image(instance, filename):
    return f"user/{instance.id}/{filename}"

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    image = models.ImageField(upload_to=user_image, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
    
    @property
    def posts(self):
        return self.post_set.all()

# ----------------------------------------------------------------
# USER-POST
# ----------------------------------------------------------------
# from userapp.models import User

def post_image(instance, filename):
    return f"post/{instance.id}/{filename}"

class Post(models.Model):
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to=post_image, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_set', blank=True, verbose_name='Likes')

    dislikes = models.ManyToManyField(User, related_name='dislikes_set', blank=True, verbose_name='Dislikes')


    def __str__(self):
        return f"{self.author.username} - {self.id}"

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'



# ----------------------------------------------------------------
# USER-COMMENT
# ----------------------------------------------------------------
# from userapp.models import Post
# from django.contrib.auth import get_user_model

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    comment_likes = models.ManyToManyField(User, related_name='comment_likes', blank=True, verbose_name='Comment_Likes')
    comment_dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True, verbose_name='Comment_Dislikes')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.description} post"