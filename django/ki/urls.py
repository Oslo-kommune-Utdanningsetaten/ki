from django.urls import path
from .views import api, auth, routes

routeurls = [
  # Main:
  path("", routes.index, name='main.index'),
  path("bot/<int:bot_nr>", routes.bot, name='main.bot'),
  path("adminbot/<str:bot_nr>", routes.adminbot, name="main.adminbot"),
  path("adminbot/<int:bot_nr>", routes.adminbot, name="main.adminbot"),
  path("settings/", routes.settings, name="main.settings"),

  # Info:
  path("info/om", routes.info, name="info.om"),
]

authurls = [
  path("feidelogin/", auth.feidelogin, name="auth.feidelogin"),
  path("auth/feidecallback", auth.feidecallback, name="feidecallback"),
  path("logout/", auth.logout, name="auth.logout")
]

apiurls = [
  path("api/bot/<int:bot_nr>", api.start_message, name="api.start_message"),
  path("api/send_message", api.send_message, name="api.send_message")
]

urlpatterns = routeurls + authurls + apiurls
