from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import serializers
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
from .permissions import IsAuthorOrReadOnly
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


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
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
        serializer.is_valid(raise_exeption=True)
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
        font_name = 'Handicraft'
        final_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__carts__user=request.user
        ).values_list(
                'ingredient__name',
                'ingredient__measurement_unit',
                'amount'
        )
        for ing in ingredients:
            name = ing[0]
            measurement_unit = ing[1]
            amount = ing[2]
            if ing['name'] in final_list:
                final_list[name]['amount'] += amount
            else:
                final_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
        pdfmetrics.registerFont(
            TTFont(font_name, 'data/' + font_name, 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont(font_name, size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont(font_name, size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(
                75, 
                height,
                '{}. {} - {} {}'.format(
                    i, name, data['amount'], data['measurement_unit']
                )
            )
        page.showPage()
        page.save()
        return response
