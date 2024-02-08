from django.urls import path
from .views import RegisterUser, LoginUser, CustomObtainTokenPairView

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('token/', CustomObtainTokenPairView.as_view(), name='token_obtain_pair'),
]