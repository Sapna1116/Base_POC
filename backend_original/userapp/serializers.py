from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Post, Comment

# Mixin for handling post count
class PostCountMixin:
    posts_count = serializers.SerializerMethodField()

    def get_posts_count(self, obj):
        # posts is @property
        return obj.posts.count()

# ----------------------------------------------------------------
# USER-COMMENT
# ----------------------------------------------------------------

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_image = serializers.ReadOnlyField(source='author.image.url')
    post = serializers.ReadOnlyField(source='post.description')

    # post = serializers.ReadOnlyField()
    comment_likes = serializers.SerializerMethodField()
    comment_dislikes = serializers.SerializerMethodField()

    def get_comment_likes(self, obj):
        return [user.username for user in obj.comment_likes.all()]

    def get_comment_dislikes(self, obj):
        return [user.username for user in obj.comment_dislikes.all()]


    class Meta:
        model = Comment
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'



# ----------------------------------------------------------------
# USER-POST
# ----------------------------------------------------------------

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_image = serializers.ReadOnlyField(source='author.image.url')
    # author_image = serializers.SerializerMethodField()
    author_id = serializers.ReadOnlyField(source='author.id')
    likes = serializers.SerializerMethodField()

    dislikes = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        # extra_kwargs = {"author" : {"read_only":True}}


    # def get_author_image(self, obj):
    #     return obj.author.image.url if obj.author.image else None
    

    def get_likes(self, obj):
        return [user.username for user in obj.likes.all()]

   
    def get_dislikes(self, obj):
        return [user.username for user in obj.dislikes.all()]


    # Env
    def get_image(self, obj):
        return obj.image.url.replace('http://localhost:8000', '')
        # return obj.image.url.replace('http://localhost:8000', '') if obj.image else None


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


# ----------------------------------------------------------------
# USER-AUTH
# ----------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    class Meta:
        model = User
        exclude = ('password',)
        # extra_kwargs = {"password" : {"write_only":True}}
    
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'bio', 'image',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(required=True, write_only=True, min_length=5)
    password2 = serializers.CharField(required=True, write_only=True, min_length=5)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        else:
            return data

class SearchUserSerializer(serializers.ModelSerializer, PostCountMixin):
    posts_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'image', 'posts_count',)

class UserLoggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'image',)

    
# ==================== AUTH ====================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # return a dictionary data with keys "access" and "refresh"
    pass

