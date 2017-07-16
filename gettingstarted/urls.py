from django.conf.urls import include, url

import hello.views
from hello.views import chatbot
# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    #url(r'^$', hello.views.fb_webhook, name='index'),
    url(r'^fb_bot/?$', chatbot.as_view(), name='test'),
    #url(r'^db', hello.views.db, name='db'),

]
