import os
import json
from aiohttp import web

class AppSettings():
    def __init__(self, user_manager):
        self.user_manager = user_manager  # 用户管理器实例

    def get_settings(self, request):
        """
        获取用户的设置，如果文件存在，则从文件中读取设置，否则返回空字典。
        """
        file = self.user_manager.get_request_user_filepath(
            request, "comfy.settings.json")
        if os.path.isfile(file):
            with open(file) as f:
                return json.load(f)
        else:
            return {}

    def save_settings(self, request, settings):
        """
        将用户的设置保存到文件中。
        """
        file = self.user_manager.get_request_user_filepath(
            request, "comfy.settings.json")
        with open(file, "w") as f:
            f.write(json.dumps(settings, indent=4))

    def add_routes(self, routes):
        """
        添加路由以处理设置相关的HTTP请求。
        """
        @routes.get("/settings")
        async def get_settings(request):
            """
            处理获取所有设置的GET请求。
            """
            return web.json_response(self.get_settings(request))

        @routes.get("/settings/{id}")
        async def get_setting(request):
            """
            处理获取单个设置的GET请求。
            """
            value = None
            settings = self.get_settings(request)
            setting_id = request.match_info.get("id", None)
            if setting_id and setting_id in settings:
                value = settings[setting_id]
            return web.json_response(value)

        @routes.post("/settings")
        async def post_settings(request):
            """
            处理更新多个设置的POST请求。
            """
            settings = self.get_settings(request)
            new_settings = await request.json()
            self.save_settings(request, {**settings, **new_settings})
            return web.Response(status=200)

        @routes.post("/settings/{id}")
        async def post_setting(request):
            """
            处理更新单个设置的POST请求。
            """
            setting_id = request.match_info.get("id", None)
            if not setting_id:
                return web.Response(status=400)
            settings = self.get_settings(request)
            settings[setting_id] = await request.json()
            self.save_settings(request, settings)
            return web.Response(status=200)
