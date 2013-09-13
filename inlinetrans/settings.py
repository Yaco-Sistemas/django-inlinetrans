# Copyright (c) 2010-2013 by Yaco Sistemas <ant30tx@gmail.com> or <goinnn@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this programe.  If not, see <http://www.gnu.org/licenses/>.

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
DEFAULT_USER_CAN_TRANSLATE = lambda user: user.is_staff


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


def get_user_can_translate(user):
    from django.conf import settings
    if hasattr(settings, 'USER_CAN_TRANSLATE'):
        return settings.USER_CAN_TRANSLATE(user)
    else:
        return DEFAULT_USER_CAN_TRANSLATE(user)
