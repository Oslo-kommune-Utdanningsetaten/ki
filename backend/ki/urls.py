from django.urls import path
from .views import api, auth


authurls = [
  path("auth/feidelogin/", auth.feidelogin, name="auth.feidelogin"),
  path("auth/feidecallback", auth.feidecallback, name="feidecallback"),
  path("auth/logout/", auth.logout, name="auth.logout"),
  path("auth/logged_out/", auth.logged_out, name="auth.logged_out"),
]

apiurls = [
  path("api/bot/<int:bot_nr>", api.start_message, name="api.start_message"),
  path("api/send_message", api.send_message, name="api.send_message"),
  path("api/favorite/<int:bot_nr>", api.favorite, name="api.favorite"),
  path("api/user_bots", api.user_bots, name="api.user_bots"),
  path("api/bot_info/", api.bot_info, name="api.bot_info"),
  path("api/bot_info/<int:bot_nr>", api.bot_info, name="api.bot_info"),
  path("api/bot_groups/", api.bot_groups, name="api.bot_groups"),
  path("api/bot_groups/<int:bot_nr>", api.bot_groups, name="api.bot_groups"),
  path("api/bot_access/", api.bot_access, name="api.bot_access"),
  path("api/bot_access/<int:bot_nr>", api.bot_access, name="api.bot_access"),
  path("api/settings", api.settings, name="api.settings"),
  path("api/school_access", api.school_access, name="api.school_access"),
  path("api/menu_items", api.menu_items, name="api.menu_items"),
  path("api/page_text/<str:page>", api.page_text, name="api.page_text"),
]

urlpatterns = authurls + apiurls
