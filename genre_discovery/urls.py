from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
