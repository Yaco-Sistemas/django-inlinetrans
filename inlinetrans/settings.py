"""

You have to define an AUTO_RELOAD_METHOD in your settings or
DEFAULT_AUTO_RELOAD_METHOD will be used.

Options for this settings::
  * "test" for a django instance (this do a touch over settings.py for reload)
  * "apache2"
  * "httpd"
  * "wsgi"
  * "restart_script <script_path_name>"

"""
DEFAULT_AUTO_RELOAD_METHOD = 'test'
DEFAULT_AUTO_RELOAD_TIME = '5'
DEFAULT_AUTO_RELOAD_LOG = 'var/log/autoreload_last.log'


def get_auto_reload_method():
    from django.conf import settings
    if hasattr(settings, 'AUTO_RELOAD_METHOD'):
        return settings.AUTO_RELOAD_METHOD
    else:
        return DEFAULT_AUTO_RELOAD_METHOD


def get_auto_reload_time():
    from django.conf import settings
    if hasattr(settings, 'AUTO_RELOAD_TIME'):
        return settings.AUTO_RELOAD_TIME
    else:
        return DEFAULT_AUTO_RELOAD_TIME


def get_auto_reload_log():
    from django.conf import settings
    if hasattr(settings, 'AUTO_RELOAD_LOG'):
        return settings.AUTO_RELOAD_LOG
    else:
        return DEFAULT_AUTO_RELOAD_LOG
