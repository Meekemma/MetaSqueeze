from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .throttles import RegisterThrottle, LoginThrottle, LogoutThrottle
from rest_framework.permissions import IsAuthenticated
from .serializers import RegistrationSerializer,LoginSerializer
from .utils import send_verification_email
from django.contrib.auth.tokens import default_token_generator
# JWT authentication imports
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model

User = get_user_model()



@api_view(['POST'])
@throttle_classes([RegisterThrottle])
def registration_view(request):
    """
    Handles user registration via POST request.
    Validates and saves the user using RegistrationSerializer.
    """
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Save the validated user data
    user = serializer.save()
    send_verification_email(user, request)
    

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




@api_view(['GET'])
def verify_email(request, uidb64, token):
    """
    Verifies the user's email using the token sent in the verification email.
    """
    User = get_user_model()
    try:
        user = User.objects.get(pk=uidb64)
        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)



@throttle_classes([LoginThrottle])
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
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([LogoutThrottle])
def logout_view(request):
    """
    Logs out a user by blacklisting their refresh token.
    This prevents the token from being reused to generate a new access token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create a RefreshToken instance from the provided token
        token = RefreshToken(refresh_token)

        # Blacklist the token to prevent reuse
        token.blacklist()  
        
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
    except TokenError:
        # Handle cases where the token is invalid or expired
        return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

