from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView,\
    CreateRecipeView, ReviewCreateView, BestAvgRatingView, SelectUserRecipesView, \
    ReviewUpdateDeleteView, RecipeUpdateDeleteView


urlpatterns = [
    path('register', RegisterView.as_view()), # Richiede name, email e password  POST
    path('login', LoginView.as_view()), # Richiede email e password  POST
    path('user', UserView.as_view()), # Restutisce i dati dell'utente loggato GET
    path('logout', LogoutView.as_view()), # Logout dell'utente loggato  POST
    path('createrecipe', CreateRecipeView.as_view()), # Richiede title e ingredients  POST
    path('createreview', ReviewCreateView.as_view()), # Richiede recipe id, review e rating  POST
    path('avgreciperating', BestAvgRatingView.as_view()), # Restituisce le ricette ordinate per rating medio  GET
    path('userrecipes', SelectUserRecipesView.as_view()), # Restituisce le ricette dell'utente scelto, richiede author POST
    path('updatereview', ReviewUpdateDeleteView.as_view()),  # Richiede review id, review(commento) e rating PUT // Richiede review id  DELETE
    path('updaterecipe', RecipeUpdateDeleteView.as_view())  # Richiede recipe id, title e ingredients PUT // Richiede recipe id  DELETE
]
