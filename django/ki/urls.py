from django.urls import path
from .views import routes

routeurls = [
    # Main:
    path("", routes.index, name='main.index'),
    path("bot/", routes.bot, name='main.bot'),
    path("adminbot/<str:bot_nr>", routes.adminbot, name="main.adminbot"),
    path("adminbot/<int:bot_nr>", routes.adminbot, name="main.adminbot"),

    # WIP:
    path("wip/", routes.wip, name="main.settings"),
    path("wip/", routes.wip, name="auth.feidelogin"),
    path("wip/", routes.wip, name="auth.logout"),
    path("wip/", routes.wip, name="info.om"),
]

urlpatterns = routeurls
