from django.conf.urls import patterns, include, url
from django.contrib import admin

from truco import views

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^truco/', include('truco.urls', namespace='truco')),
    url(r'^login/$', 'django.contrib.auth.views.login', name= 'login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^sign-up/$', views.sign_up, name='sign-up'),
)