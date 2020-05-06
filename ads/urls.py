from django.urls import path

from ads import views

app_name = 'ads'
urlpatterns = [
    path('', views.index(), name='index'),
    path('ads/<str:category>/<str:subcategory>', views.ads_by_categories.as_view(), name='list_by_categories'),
    path('<str:ad_slug>/', views.detail, name='detail'),
    path('create', views.create, name='create'),

]
