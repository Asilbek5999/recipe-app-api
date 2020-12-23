from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('tags', viewset=TagViewSet)
router.register("ingredient", viewset=IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
