from rest_framework.routers import DefaultRouter
from produtos.views import ProdutoViewSet, CategoriaViewSet

router = DefaultRouter()

# Rotas
router.register(r'produtos', ProdutoViewSet, basename='produtos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')

urlpatterns = router.urls