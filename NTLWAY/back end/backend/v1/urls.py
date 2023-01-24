from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework_simplejwt import views as jwt_views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    
    path('register', views.Register.as_view(), name='register'),
    path('login', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('devis', views.ListDevis.as_view()),
    path('devis/<str:pk>', views.DevisDetail.as_view()),
    path('status/<str:pk>', views.DevisStatus.as_view()),
    path('send/<str:pk>',views.DevisSendCRM.as_view()),
    path('devis/<str:pk>/download', views.DevisDownload.as_view()), # become /download
    path('lettre/<str:pk>/download', views.LettreDownload.as_view()), # become /download
    path('devis/<str:pk>/send', views.DevisSend.as_view()), #send mail  : pdf => mail in database  + update status to sent
    path('devis/calculate', views.DevisCalculate.as_view()),
    path('devisrefresh', views.DevisRefresh.as_view()),
    path('users', views.ListUser.as_view()),
    path('users/current', views.CurrentUser.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view()),
    path('users/delete/<int:pk>', views.UserDelete.as_view()),
    path('users/change_password/<int:pk>', views.ChangePassword.as_view())
]