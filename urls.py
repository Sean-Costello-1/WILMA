from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webapp/', include('webapp.urls'))
]
