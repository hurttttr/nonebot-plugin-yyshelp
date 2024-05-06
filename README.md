# yyshelp

## How to start

1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `yyshelp/plugins` folder.
4. run your bot using `nb run --reload` .

## Documentation

See [Docs](https://nonebot.dev/)

需要安装的库：request,pillow

目前使用的api国内无法访问，请自行解决，如果代理导致无法正常使用，请安装

```shell
.vnev/bin/pip3 install httpx[socks] requests[socks]
```

xyzwhelp需配置中添加`xyzwhelp_apikey`在ocr.space自行申请，如果使用其他api自行 修改`utils/get.py`文件中的`ocr_space_file`函数

### 当前所用插件以及需额外安装的部分

```shell
nb plugin install nonebot-plugin-autoreply nonebot-bison nonebot-plugin-send-anything-anywhere nonebot-plugin-learning-chat nonebot-plugin-naturel-gpt nonebot_plugin_memes nonebot_plugin_kawaii_status
pip install --force-reinstall 'pydantic~=1.10' #降级
pip install --upgrade 'openai>=1.0' #升级
pip install requests pillow
```

