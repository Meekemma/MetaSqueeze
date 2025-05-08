from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import RegistrationSerializer,LoginSerializer

# JWT authentication imports
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
def registration_view(request):
    """
    Handles user registration via POST request.
    Validates and saves the user using RegistrationSerializer.
    """
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Save the validated user data
    user = serializer.save()

    # Prepare a safe response (excluding sensitive fields)
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    return Response({
        'message': 'User created successfully!',
        'data': user_data
    }, status=status.HTTP_201_CREATED)




@api_view(['POST'])
def login_view(request):
    """
    Handles user login via POST request and returns JWT tokens.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "full_name": f"{user.first_name} {user.last_name}",
            "user_id": user.id,
            "email": user.email,
            "is_verified": user.is_verified,
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    