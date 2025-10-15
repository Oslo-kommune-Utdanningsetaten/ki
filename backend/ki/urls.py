from django.urls import path
from .views import api, auth


authurls = [
    path("auth/feidelogin/", auth.feidelogin, name="auth.feidelogin"),
    path("auth/locallogin/", auth.locallogin, name="auth.locallogin"),
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
    path("api/user_info/", api.user_info, name="api.user_info"),
    path("api/external_users/", api.external_users, name="api.external_users"),
    path("api/external_user/", api.external_user_create, name="api.external_user_create"),
    path("api/external_user/<int:user_id>", api.external_user, name="api.external_user"),
    path(
        "api/external_user_self_service/", api.external_user_self_service,
        name="api.external_user_self_service"),
    path("api/settings", api.settings, name="api.settings"),
    path("api/school_access", api.school_access, name="api.school_access"),
    path("api/school_list", api.school_list, name="api.school_list"),
    path("api/author/", api.author_create, name="api.author_create"),
    path("api/author/<str:user_id>", api.author, name="api.author"),
    path("api/authors", api.authors, name="api.authors"),
    path("api/app_config", api.app_config, name="api.app_config"),
    path("api/info_page/", api.create_info_page, name="api.create_info_page"),
    path("api/info_page/<str:slug>", api.info_page, name="api.info_page"),
    path("api/upload_info_image", api.upload_info_image, name="api.upload_info_image"),
]

urlpatterns = authurls + apiurls
