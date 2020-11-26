from django.urls import path
from core.views import show_main_page, edit_line, stop_line, AJAX_test, refresh_page, install_default, turn_on

urlpatterns = [
    path('', show_main_page, name='show_main_page'),

    path('edit_page/', edit_line, name='edit_line'),
    path('stop_page/', stop_line, name='stop_line'),
    path('test/', AJAX_test),
    path('refresh_page/', refresh_page, name='refresh_page'),
    path('install_default/', install_default, name='install_default'),
    path('turn_on/', turn_on, name='turn_on'),
]
