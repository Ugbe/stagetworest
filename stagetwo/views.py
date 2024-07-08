from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    OrganisationSerializer,
    AddUserToOrganisationSerializer
)
from .models import User, Organisation



def get_tokens_for_user(user):
    refresh = AccessToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            data = {
                "accessToken": token['access'],
                "user": {
                    "userId": str(user.userId),
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                }
            }
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": data
            }, status=status.HTTP_201_CREATED)
        else:
            errors = [
                {"field": field, "message": message}
                for field, messages in serializer.errors.items()
                for message in messages
            ]
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                data = {
                    "accessToken": token['access'],
                    "user": {
                        "userId": str(user.userId),
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "data": data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        current_user = request.user
        if str(current_user.userId) == user_id:
            user = current_user
        else:
            try:
                user = User.objects.get(userId=user_id)
            except User.DoesNotExist:
                return Response({
                    "status": "Bad Request",
                    "message": "User not found",
                    "statusCode": 404
                }, status=status.HTTP_404_NOT_FOUND)
            #If user does exist, check if both users belong to at least one common organisation
            commmon_organizations = Organisation.objects.filter(users=current_user).filter(users=user)
            if not commmon_organizations.exists():
                return Response({
                    "status": "Forbidden Request",
                    "message": "You do not have the permission to view this yet",
                    "statusCode": 403
                }, status=status.HTTP_403_FORBIDDEN)
        data = {
            "userId": str(user.userId),
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "phone": user.phone,
        }
        return Response({
            "status": "success",
            "message": "User retrieved successfully",
            "data": data
            }, status=status.HTTP_200_OK)
        

class OrganisationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)

class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        try:
            organisation = Organisation.objects.get(orgId=org_id, users=request.user)
            serializer = OrganisationSerializer(organisation)
            return Response({
                "status": "success",
                "message": "Organisation retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Bad request",
                "message": "Organisation not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

class OrganisationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            organisation.save()
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        serializer = AddUserToOrganisationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(userId=serializer.validated_data['userId'])
                organisation = Organisation.objects.get(orgId=org_id, users=request.user)
                organisation.users.add(user)
                organisation.save()
                return Response({
                    "status": "success",
                    "message": "User added to organisation successfully"
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    "status": "Bad request",
                    "message": "User not found",
                    "statusCode": 404
                }, status=status.HTTP_404_NOT_FOUND)
            except Organisation.DoesNotExist:
                return Response({
                    "status": "Bad request",
                    "message": "Organisation not found",
                    "statusCode": 404
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

