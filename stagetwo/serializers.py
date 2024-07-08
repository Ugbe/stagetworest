from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email, RegexValidator
from .models import Organisation
from rest_framework.validators import UniqueValidator


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    userId = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email is already registered."),
            validate_email
        ]
    )
    phone = serializers.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex = r'^(\+)?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['firstName'],
            last_name=validated_data['lastName'],
            phone=validated_data.get('phone', ''),
        )
        user.set_password(validated_data['password'])
        user.save()

        org_name = f"{user.first_name}'s Organisation"
        org = Organisation.objects.create(name=org_name)
        org.users.add(user)
        org.save()

        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']

class AddUserToOrganisationSerializer(serializers.Serializer):
    userId = serializers.UUIDField()
