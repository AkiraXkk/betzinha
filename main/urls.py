import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, re_path
from django.views.static import serve

urlpatterns = [
    re_path(r'^', include(('partidas.urls', 'partidas'), namespace='partidas')),
    re_path(r'^usuario/', include(('contas.urls', 'contas'), namespace='contas')),
    re_path(r'^apostas/', include(('apostas.urls', 'apostas'), namespace='apostas')),
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.extend([
        re_path(
            r'^docs/(?P<path>.*)$', serve,
            {'document_root': os.path.join(settings.DOCS_ROOT, 'build/html/'),
             'show_indexes': False}
        ),
        re_path(
            r'^static/(?P<path>.*)$', serve,
            {'document_root': os.path.join(settings.STATIC_ROOT),
             'show_indexes': False}
        )
    ])
    try:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
