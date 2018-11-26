from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listAppend', views.listAppend, name ='listAppend'),
    path('listDelete', views.listDelete, name ='listDelete'),
    path('triggerDraw',views.triggerDraw,name='triggerDraw'),
    path('drawResult',views.draw,name='drawResult')
]