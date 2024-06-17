from userapp.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# To create the access and the refresh tokens.
# And it's going to create this token "only" if:- a valid username and password are provided.
# When decoding the access token: it's going to give us the username and the email and anything that we pass in there
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        
        token = super().get_token(user)
        
        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        # Image must be passed as a str to be able to be serialized into JSON format
        token['image'] = str(user.profile.image)
        token['verified'] = user.profile.verified
        # ...
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=5, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, min_length=5)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
            # Didn't put pwd field here since it's not a field in the User model, hence would have gave error
        )
        # To store pwd in a hashable format
        user.set_password(validated_data['password'])
        user.save()

        return user


class SearchUserSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('username', 'email')


class UserLoggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
