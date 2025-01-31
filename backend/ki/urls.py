from django.urls import path
from .views import api, auth


authurls = [
  path("auth/feidelogin/", auth.feidelogin, name="auth.feidelogin"),
  path("auth/feidecallback", auth.feidecallback, name="feidecallback"),
  path("auth/logout/", auth.logout, name="auth.logout"),
  path("auth/logged_out/", auth.logged_out, name="auth.logged_out"),
]

apiurls = [
  path("api/bot/<uuid:uuid>", api.start_message, name="api.start_message"),
  path("api/send_message", api.send_message, name="api.send_message"),
  path("api/send_img_message", api.send_img_message, name="api.send_img_message"),
  path("api/favorite/<uuid:bot_uuid>", api.favorite, name="api.favorite"),
  path("api/user_bots", api.user_bots, name="api.user_bots"),
  path("api/bot_models", api.bot_models, name="api.bot_models"),
  path("api/empty_bot/<str:bot_type>", api.empty_bot, name="api.empty_bot"),
  path("api/bot_info/", api.bot_info, name="api.bot_info"),
  path("api/bot_info/<uuid:bot_uuid>", api.bot_info, name="api.bot_info"),
  path("api/settings", api.settings, name="api.settings"),
  path("api/school_access", api.school_access, name="api.school_access"),
  path("api/menu_items", api.menu_items, name="api.menu_items"),
  path("api/page_text/<str:page>", api.page_text, name="api.page_text"),
]

urlpatterns = authurls + apiurls
