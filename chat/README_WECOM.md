# 企业微信群机器人复读机

这是一个企业微信群机器人的复读机实现，用户向机器人发什么，机器人就返回什么。

## 功能特点

- 🔁 **完美复读**: 文本消息原样返回
- 🖼️ **图文支持**: 图文混排消息提取文字部分复读
- 🔒 **安全加密**: 支持企业微信标准加密解密
- 📱 **多场景**: 支持群聊、单聊、小黑板
- 🛡️ **消息去重**: 自动去重，避免重复处理
- ⚡ **实时响应**: 实时接收和回复消息

## 支持的消息类型

| 消息类型 | 处理方式 | 说明 |
|---------|----------|------|
| 文本消息 | 原样复读 | 完全复读用户发送的文字内容 |
| 图片消息 | 友好提示 | 提示不支持图片复读 |
| 图文混排 | 提取文字 | 只复读其中的文字部分 |
| 事件消息 | 欢迎语 | 机器人加入群聊时的欢迎消息 |
| 按钮点击 | 确认提示 | 确认收到按钮点击事件 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置机器人

运行配置向导：
```bash
python wecom_config.py
```

或直接运行启动脚本（会自动启动配置向导）：
```bash
python run_wecom_bot.py
```

### 3. 企业微信后台配置

1. 登录企业微信管理后台
2. 进入 **应用管理** > **群机器人**
3. 创建新的群机器人或编辑现有机器人
4. 设置以下参数：
   - **URL**: `http://你的域名或IP:8080/wecom/callback`
   - **Token**: 运行配置向导时设置的Token
   - **EncodingAESKey**: 运行配置向导时设置的EncodingAESKey

### 4. 启动机器人

```bash
python run_wecom_bot.py
```

## 配置说明

### 配置文件

配置信息保存在 `wecom_config.json` 文件中：

```json
{
  "token": "你的Token",
  "encoding_aes_key": "你的EncodingAESKey",
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false
  },
  "callback_url": "/wecom/callback",
  "features": {
    "enable_image_tips": true,
    "enable_event_responses": true,
    "enable_mixed_text_extract": true
  }
}
```

### 重要参数说明

- **Token**: 3-32位英文或数字，用于生成签名验证
- **EncodingAESKey**: 43位英文或数字，用于消息加解密
- **host**: 服务监听地址，0.0.0.0表示监听所有网卡
- **port**: 服务端口，默认8080

## API接口

### 回调接口

- **URL**: `/wecom/callback`
- **方法**: GET (URL验证) / POST (消息接收)
- **说明**: 企业微信回调接口，处理消息和事件

### 健康检查

- **URL**: `/health`
- **方法**: GET
- **返回**: 
```json
{
  "status": "healthy",
  "service": "企业微信复读机器人",
  "version": "1.0.0"
}
```

### 配置管理

- **URL**: `/config`
- **方法**: GET (查看配置) / POST (更新配置)
- **说明**: 动态查看和更新机器人配置

## 使用示例

### 文本消息复读

```
用户: 你好，机器人！
机器人: 你好，机器人！

用户: 今天天气真不错
机器人: 今天天气真不错
```

### 图文混排消息

```
用户: [发送图文混排: "这是一段文字" + 图片]
机器人: 这是一段文字
```

### 事件响应

```
[机器人被添加到群聊]
机器人: 大家好！我是复读机器人，你们说什么我就说什么~

[用户进入单聊]
机器人: 欢迎来到复读机器人！发送任何文字消息，我都会原样复读给你~
```

## 部署建议

### 本地测试

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置机器人
python wecom_config.py

# 3. 启动服务
python run_wecom_bot.py
```

### 生产部署

1. **使用HTTPS**: 企业微信推荐使用HTTPS
2. **反向代理**: 使用Nginx等反向代理
3. **进程管理**: 使用supervisor、systemd等管理进程
4. **日志管理**: 配置日志轮转和监控

#### Nginx配置示例

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    location /wecom/callback {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 故障排除

### 常见问题

1. **URL验证失败**
   - 检查Token和EncodingAESKey是否正确
   - 确认服务器能被企业微信访问
   - 检查回调URL是否正确

2. **消息解密失败**
   - 确认EncodingAESKey长度为43位
   - 检查Token是否与后台配置一致
   - 查看日志中的详细错误信息

3. **无法接收消息**
   - 确认机器人已被添加到群聊
   - 检查网络连接和防火墙设置
   - 验证回调URL是否可达

### 日志查看

机器人运行时会输出详细的日志信息：

```bash
# 启动时显示配置信息
2024-01-01 12:00:00 - INFO - URL验证请求: signature=xxx, timestamp=xxx, nonce=xxx
2024-01-01 12:00:01 - INFO - URL验证成功
2024-01-01 12:00:02 - INFO - 收到文本消息: 你好
2024-01-01 12:00:03 - INFO - 消息处理成功，返回加密回复
```

## 安全注意事项

1. **保护密钥**: 妥善保管Token和EncodingAESKey
2. **访问控制**: 限制回调URL的访问来源
3. **HTTPS**: 生产环境建议使用HTTPS
4. **日志安全**: 避免在日志中记录敏感信息

## 扩展开发

机器人代码结构清晰，易于扩展：

- `WXBizMsgCrypt`: 消息加解密类
- `WeComRepeaterBot`: 机器人核心逻辑
- `WeComConfig`: 配置管理

可以通过修改 `process_message` 方法来实现更复杂的消息处理逻辑。

## 许可证

MIT License

## 联系我们

如果有任何问题或建议，欢迎提Issue或PR。 