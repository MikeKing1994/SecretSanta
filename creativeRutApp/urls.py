from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('creativeRutApp/', views.index, name='index'),
    path('creativeRutApp/listAppend', views.listAppend, name ='listAppend'),
    path('creativeRutApp/listDelete', views.listDelete, name ='listDelete'),
    path('creativeRutApp/triggerDraw',views.triggerDraw,name='triggerDraw'),
    path('creativeRutApp/drawResult',views.draw,name='drawResult')
]