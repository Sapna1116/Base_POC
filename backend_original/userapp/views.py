
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models.query_utils import Q

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny 
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from .serializers import (
UserSerializer,
UserCreateSerializer,
ChangePasswordSerializer,
CustomTokenObtainPairSerializer,
SearchUserSerializer,
UserLoggedSerializer
)
from .pagination import CustomPagination

from .models import User


def staff_required(view_func):
    def wrapped_view(view_instance, request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(view_instance, request, *args, **kwargs)
        else:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return wrapped_view

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.get_serializer().Meta.model.objects.filter(is_active=True)
            return self.queryset
        else:
            return self.queryset
    def get_object(self, pk):
        return get_object_or_404(self.serializer_class.Meta.model, pk=pk)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        else:
            return super().get_permissions()

    def list(self, request):
        users_serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(users_serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        user_serializer = UserCreateSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = self.get_object(pk=pk)
        user_serializer = self.serializer_class(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'message': 'User updated successfully', 'data': user_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = self.serializer_class.Meta.model.objects.filter(is_active=True, pk=pk).first()
        if user:
            user_serializer = self.serializer_class(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @staff_required
    def destroy(self, request, pk=None):
        user = self.get_object(pk=pk)
        user.is_active = False
        if user.is_active == False:
            user.save()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User not deleted'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def change_password(self, request, pk=None):   
        user = self.get_object(pk=pk)
        password_serializer = ChangePasswordSerializer(data=request.data)
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data['password1']) # hash
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ==================== AUTH ====================
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password) # validated instance

        if user:
            login_serializer = self.get_serializer(data=request.data)
            if login_serializer.is_valid():
                user_serializer = UserSerializer(user)
                return Response({
                'access': login_serializer.validated_data['access'],
                'refresh': login_serializer.validated_data['refresh'],
                'user': user_serializer.data,
                'message': 'Login successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
        

class SearchUserView(APIView):
    def get(self, request):
        search_term = request.query_params.get('search')
        matches = User.objects.filter(
            Q(username__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term)
        ).distinct()

        paginator = CustomPagination()
        results = paginator.paginate_queryset(matches, request)

        user_search_serializer = SearchUserSerializer(results, many=True)
        return paginator.get_paginated_response(user_search_serializer.data)

class UserLoggedDataView(APIView):
    def get(self, request):
        user = request.user
        user_serializer = UserLoggedSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    


# ----------------------------------------------------------------
# USER-POST
# ----------------------------------------------------------------
from django.shortcuts import get_object_or_404

from .serializers import (
PostSerializer,
PostCreateSerializer,
)
from .models import Post


def is_owner(request, instance):
    return request.user == instance.author or request.user.is_staff # boolean value


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = Post.objects.all()
            return self.queryset
        else:
            return self.queryset

    def get_object(self, pk=None):
        return get_object_or_404(Post, pk=pk)

    def list(self, request):
        posts = self.serializer_class.Meta.model.objects.order_by('-id').all()
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts, request)

        posts_serializers = self.get_serializer(results, many=True)
        return paginator.get_paginated_response(posts_serializers.data)

    def create(self, request):
        post_serializer = PostCreateSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        posts = self.get_object(pk=pk)
        post_serializer = self.serializer_class(posts)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        post = self.get_object(pk=pk)
        if not is_owner(request, post):
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if 'image' not in request.data or request.data['image'] == '' or request.data['image'] == 'None':
                data = request.data.copy()
                current_image = post.image
                data['image'] = current_image

                post_serializer = PostSerializer(post, data=data)
                if post_serializer.is_valid():
                    post_serializer.save()
                    return Response({'message': 'Post updated successfully', 'data': post_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                post_serializer = PostSerializer(post, data=request.data)
                if post_serializer.is_valid():
                    post_serializer.save()
                    return Response({'message': 'Post updated successfully', 'data': post_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check if 'image' is not provided or empty
        # if 'image' not in request.data or request.data['image'] == '':
        #     data = request.data.copy()
        #     current_image = post.image
        #     data['image'] = current_image
        #     post_serializer = PostSerializer(post, data=data)
        # else:
        #     post_serializer = PostSerializer(post, data=request.data)
        
        # if post_serializer.is_valid():
        #     post_serializer.save()
        #     return Response({'message': 'Post updated successfully', 'data': post_serializer.data}, status=status.HTTP_200_OK)
        # else:
        #     return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        post = self.get_object(pk=pk)
        if not is_owner(request, post):
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            post.delete()
            return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)

# class PostLikeView(APIView):
#     def post(self, request, postId):
#         try:
#             # post.likes += 1
#             post = get_object_or_404(Post, pk=postId)
#             post.likes.add(request.user)
#             return Response({'message': 'Post liked successfully'}, status=status.HTTP_200_OK)
#         except Post.DoesNotExist:
#             return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

# class PostRemoveLikeView(APIView):
#     def delete(self, request, postId):
#         try:
#             post = get_object_or_404(Post, pk=postId)
#             post.likes.remove(request.user) 
#             return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
#         except Post.DoesNotExist:
#             return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

class PostLikeView(APIView):
    def post(self, request, postId):
        try:
            # post.likes += 1
            post = get_object_or_404(Post, pk=postId)
            if request.user in post.dislikes.all():
                post.dislikes.remove(request.user) 
            post.likes.add(request.user)
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

class PostRemoveLikeView(APIView):
    def delete(self, request, postId):
        try:
            post = get_object_or_404(Post, pk=postId)
            if request.user in post.likes.all():
                post.likes.remove(request.user) 
                return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)
        

class PostDislikeView(APIView):
    def post(self, request, postId):
        try:
            # post.dislikes += 1
            post = get_object_or_404(Post, pk=postId)
            if request.user in post.likes.all():
                post.likes.remove(request.user) 
            post.dislikes.add(request.user)
            return Response({'message': 'Post disliked successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

class PostRemoveDislikeView(APIView):
    def delete(self, request, postId):
        try:
            post = get_object_or_404(Post, pk=postId)
            if request.user in post.dislikes.all():
                post.dislikes.remove(request.user) 
                return Response({'message': 'Post undisliked successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You have not disliked this post'}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)


# ----------------------------------------------------------------
# USER-COMMENT
# ----------------------------------------------------------------
from .serializers import CommentSerializer, CommentCreateSerializer
from .models import Comment

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.get_serializer().Meta.model.objects.all()
            return self.queryset
        else:
            return self.queryset

    def create(self, request):
        comment_serializer = CommentCreateSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    # def destroy(self, request, pk=None):
    #     try:
    #         comment = get_object_or_404(Comment, pk=pk)
    #         if not self.request.user == comment.author and not self.request.user.is_staff:
    #             return Response({'message': 'You are not authorized to delete this comment'}, status=status.HTTP_401_UNAUTHORIZED)
    #         comment.delete()
    #         return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)
    #     except Comment.DoesNotExist:
    #         return Response({'message': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)

class CommentLikeView(APIView):
    def post(self, request, commentId):
        try:
            comment = get_object_or_404(Comment, pk=commentId)
            if request.user in comment.comment_dislikes.all():
                comment.comment_dislikes.remove(request.user)
            comment.comment_likes.add(request.user)
            return Response({'message': 'Comment liked successfully'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)

class CommentRemoveLikeView(APIView):
    def delete(self, request, commentId):
        try:
            comment = get_object_or_404(Comment, pk=commentId)
            if request.user in comment.comment_likes.all():
                comment.comment_likes.remove(request.user)
                return Response({'message': 'Comment unliked successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You have not liked this comment'}, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)

class CommentDislikeView(APIView):
    def post(self, request, commentId):
        try:
            comment = get_object_or_404(Comment, pk=commentId)
            if request.user in comment.comment_likes.all():
                comment.comment_likes.remove(request.user)
            comment.comment_dislikes.add(request.user)
            return Response({'message': 'Comment disliked successfully'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)

class CommentRemoveDislikeView(APIView):
    def delete(self, request, commentId):
        try:
            comment = get_object_or_404(Comment, pk=commentId)
            if request.user in comment.comment_dislikes.all():
                comment.comment_dislikes.remove(request.user)
                return Response({'message': 'Comment undisliked successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You have not disliked this comment'}, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment does not exist'}, status=status.HTTP_404_NOT_FOUND)