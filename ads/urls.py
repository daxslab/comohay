from django.urls import path

from ads import views

app_name = 'ads'
urlpatterns = [
    path('', views.IndexView(), name='index'),
    path('ads/<str:category>/<str:subcategory>', views.AdsByCategoriesView.as_view(), name='list_by_categories'),
    path('ads/<str:category>', views.AdsByMainCategoryView.as_view(), name='list_by_main_category'),
    path('<str:ad_slug>/', views.detail, name='detail'),
    path('create', views.create, name='create'),

]
