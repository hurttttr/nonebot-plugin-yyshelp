<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./image/README/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
</div>
<div align="center">
    ✨ 痒痒鼠们自己的机器人 ✨<br/>
    🧬 支持AI、消息推送等多种使用功能 ⚙️<br/>
    🎆 如果喜欢请点个⭐吧！您的支持就是我持续更新的动力 🎉<br/>
</div>

## 🎁 安装命令

> 安装完成后执行以下命令进行部分的库的安装以及升降级
>
> 部分插件的安装步骤和使用请参考插件原文档

```shell
nb plugin install nonebot-plugin-autoreply nonebot-bison nonebot-plugin-send-anything-anywhere nonebot_plugin_memes 
#nonebot-plugin-naturel-gpt 考虑升级至nekro-agent
.venv/bin/python -m pip install httpx[socks] requests[socks]
.venv/bin/python -m pip install --force-reinstall 'pydantic~=1.10' #降级
.venv/bin/python -m pip install --upgrade 'openai>=1.0' #升级
.venv/bin/python -m pip install requests pillow

# nonebot_plugin_memes安装依赖
sudo apt install fonts-noto-cjk fonts-noto-color-emoji
#上传字体文件到 /usr/share/fonts
fc-cache -f -v #刷新缓存

#反向ws地址
ws://127.0.0.1:5701/onebot/v11/ws
#抽签功能使用git clone安装，并修改utils.py,或者将pillow降级到9.1.0版本，推荐进行代码修改
ttfront = ImageFont.truetype(fontPath["title"], font_size)
#font_length = ttfront.getsize(title)
font_length = ttfront.getbbox(title)
draw.text(
    (
        #image_font_center[0] - font_length[0] / 2,
        #image_font_center[1] - font_length[1] / 2,
        image_font_center[0] - (font_length[2] - font_length[0]) / 2,
        image_font_center[1] - (font_length[3] - font_length[1]) / 2,
    ),
    title,
    fill=color,
    font=ttfront,
)
```

> 附带的咸鱼之王插件需配置中添加`xyzwhelp_apikey`在ocr.space自行申请，如果使用其他api自行 修改`utils/get.py`文件中的`ocr_space_file`函数
>
> 注：Python>=3.10使用requests请求https请求有问题，需执行`pip install urllib3==1.26.5`

## 💡 功能列表

> 以下未勾选功能仅表示未来可能开发的方向，不代表实际规划进度，具体开发事项可能随时变动
> 勾选: 已实现功能；未勾选: 正在开发 / 计划开发 / 待定设计

- [x] 消息推送
  - [ ] 重构功能
  - [ ] 实现在线更新

- [x] 模拟抽卡
  - [x] 抽卡图片生成
  - [x] 每周三定时查询更新
- [ ] 寮三十查询
  - [ ] 完善cookie获取方式（希望有大佬帮助）



## 📄 使用文档

尚在制作中~

## ✏️开发环境

> 推荐使用vscode，安装Black Formatter+Pylint+isort
>
> 配置过程参考：[在VSCode中编写python代码，代码规范工具介绍与推荐](https://blog.csdn.net/shiwanghualuo/article/details/131750278)

```shell
#开发环境,有版本冲突请提issue
pip install -r development.txt
```

## 🎢 更新日志

<details>
<summary>点击展开</summary>

### [2024/7/26] v1.1.1 今日老婆功能修正


- 添加今日老婆插件
- 按群友要求进行了部分修改

### [2024/7/3] v1.1.0 抽卡模块上线


- 抽卡功能实现
- 确定项目整体结构

### [2024/6/28] v1.0.0 机器人发布

- 完善项目说明

</details>

### 🎉鸣谢

感谢[nonebot-plugin-today-waifu](https://github.com/glamorgan9826/nonebot-plugin-today-waifu)项目的实现

