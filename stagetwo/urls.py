from django.urls import path
from .views import (
    UserRegistrationView, 
    UserLoginView, 
    UserDetailView, 
    OrganisationListView, 
    OrganisationDetailView, 
    OrganisationCreateView, 
    AddUserToOrganisationView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('organisations/', OrganisationListView.as_view(), name='organisation-list'),
    path('organisations/<uuid:org_id>/', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('organisations/', OrganisationCreateView.as_view(), name='organisation-create'),
    path('organisations/<uuid:org_id>/users/', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
]
