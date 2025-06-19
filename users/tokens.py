from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to access token
        token['role'] = user.role
        if user.role == "ADMIN":
            token['name'] = "Admin"
        else:
            try:
                token['name'] = user.candidate_profile.name
            except:
                token['name'] = "Candidate"

        return token
