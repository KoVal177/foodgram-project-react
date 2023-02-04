from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorites,
                            Ingredient,
                            IngredientAmount,
                            Recipe,
                            ShoppingCart,
                            Tag)
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (FavoriteSerializer,
                          IngredientSerializer,
                          RecipeListSerializer,
                          RecipeSerializer,
                          ShoppingCartSerializer,
                          TagSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorites
        )

    @action(detail=True,
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart
        )

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        FONT_NAME = 'Handicraft'
        FONT_SIZE_HEADER = 24
        FONT_SIZE_ROW = 16
        HEADER_HORIZONTAL_POS = 200
        HEADER_VERTICAL_POS = 800
        ROW_HORIZONTAL_POS = 75
        ROW_VERTICAL_POS_START = 750
        ROWS_SPACING = 25
        HEADER = 'Список покупок'
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
        ).annotate(amount = Sum('amount'))

        pdfmetrics.registerFont(
            TTFont(FONT_NAME, f'data/{FONT_NAME}.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont(FONT_NAME, size=FONT_SIZE_HEADER)
        page.drawString(HEADER_HORIZONTAL_POS,
                        HEADER_VERTICAL_POS,
                        HEADER)
        page.setFont(FONT_NAME, size=FONT_SIZE_ROW)
        height = ROW_VERTICAL_POS_START
        for i, data in enumerate(ingredients, 1):
            page.drawString(
                ROW_HORIZONTAL_POS,
                height,
                '{}. {} - {} {}'.format(
                    i,
                    data['ingredient__name'],
                    data['amount'],
                    data['ingredient__measurement_unit']
                )
            )
            height -= ROWS_SPACING
        page.showPage()
        page.save()
        return response
