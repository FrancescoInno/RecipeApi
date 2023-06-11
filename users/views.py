from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound
from .serializers import UserSerializer, RecipeSerializer, ReviewSerializer
from .models import User, Recipe, Review
from django.db.models import Avg
import jwt
import datetime


"""class AllUsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)"""


class SelectUserRecipesView(APIView):
    def post(self, request):
        user_id = request.data.get('author')

        recipes = Recipe.objects.filter(author=user_id)

        if not recipes:
            return Response({'message': 'Nessuna ricetta disponibile'})

        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)


class BestAvgRatingView(APIView):
    def get(self, request):
        recipes = Recipe.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')

        if not recipes:
            return Response({'message': 'Nessuna ricetta disponibile'})

        data = []
        for recipe in recipes:
            if recipe.avg_rating is None:
                recipe.avg_rating = "Nessuna recensione disponibile"
            recipe_data = {
                'recipe': RecipeSerializer(recipe).data,
                'avg_rating': recipe.avg_rating
            }
            data.append(recipe_data)

        return Response(data)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()

        if 'jwt' in request.COOKIES:
            response.delete_cookie('jwt')
            response.data = {
                'message': 'success'
            }
        else:
            response.data = {
                'message': 'Already logged out!'
            }

        return response


class CreateRecipeView(APIView):
    def post(self, request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        author_id = user.id
        title = request.data.get('title')
        ingredients = request.data.get('ingredients')

        data = {
            'title': title,
            'ingredients': ingredients,
            'author': author_id
        }

        serializer = RecipeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RecipeUpdateDeleteView(APIView):
    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        re_id = request.data.get('id')
        recipe = Recipe.objects.filter(id=re_id).first()

        if recipe is None:
            raise NotFound('Recipe not found!')

        if recipe.author.id != user.id:
            raise AuthenticationFailed('You do not have permission to modify this recipe')

        title = request.data.get('title')
        ingredients = request.data.get('ingredients')

        data = {
            'title': title,
            'ingredients': ingredients,
            'author': user.id
        }

        serializer = RecipeSerializer(recipe, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        re_id = request.data.get('id')
        recipe = Recipe.objects.filter(id=re_id).first()

        if recipe is None:
            raise NotFound('Recipe not found!')

        if recipe.author.id != user.id:
            raise AuthenticationFailed('You do not have permission to delete this recipe')

        recipe.delete()
        return Response({'message': 'Recipe deleted successfully'})


class ReviewCreateView(APIView):
    def post(self, request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        user_id = user.id
        recipe_review_id = request.data.get('recipe')
        review = request.data.get('review')
        rating = request.data.get('rating')

        recipe = Recipe.objects.filter(id=recipe_review_id).first()

        if recipe is None:
            raise AuthenticationFailed('Recipe not found!')

        author_recipe_id = recipe.author.id
        existing_review = Review.objects.filter(recipe=recipe_review_id, author_review=user_id).first()

        if existing_review:
            raise AuthenticationFailed('You have already reviewed this recipe!')

        if user_id == author_recipe_id:
            raise AuthenticationFailed('You cannot review your own recipe!')

        data = {
            'recipe': recipe_review_id,
            'author_review': user_id,
            'review': review,
            'rating': rating,
        }

        serializer = ReviewSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReviewUpdateDeleteView(APIView):
    def put(self, request):
        
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        user_id = user.id

        r_id = request.data.get('id')
        review = Review.objects.filter(id=r_id).first()

        if review is None:
            raise NotFound('Review not found!')

        if review.author_review.id != user_id:
            raise AuthenticationFailed('You are not authorized to update this review!')

        review_data = {
            'review': request.data.get('review'),
            'rating': request.data.get('rating'),
        }

        serializer = ReviewSerializer(review, data=review_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Not logged in!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Token!')

        user = User.objects.filter(id=payload['id']).first()
        user_id = user.id

        r_id = request.data.get('id')
        review = Review.objects.filter(id=r_id).first()

        if review is None:
            raise NotFound('Review not found!')

        if review.author_review.id != user_id:
            raise AuthenticationFailed('You are not authorized to delete this review!')

        review.delete()

        return Response({'message': 'Review deleted successfully'})
