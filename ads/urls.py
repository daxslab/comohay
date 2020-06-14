from django.urls import path
from lazysignup.decorators import allow_lazy_user

from ads import views

app_name = 'ads'
urlpatterns = [
    path('', allow_lazy_user(views.IndexView()), name='index'),
    path('url/', views.to_external_url, name='to_external_url'),
    path('ads/<str:category>/<str:subcategory>', views.AdsByCategoriesView.as_view(), name='list_by_categories'),
    path('ads/<str:category>', views.AdsByMainCategoryView.as_view(), name='list_by_main_category'),
    path('view/<str:ad_slug>/', views.detail, name='detail'),
    path('create', views.create, name='create'),
    path('edit/<int:id>', views.edit, name='edit'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('my_ads/', views.user_ads, name='user_ads'),

]
