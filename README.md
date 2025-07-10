# 易事厅第三方机器人API

基于易事厅机器人接入指南实现的支持同步流式返回的Python Flask API。

## ✨ 功能特性

- ✅ **同步流式返回** - 支持 Server-Sent Events (SSE) 格式的流式响应
- ✅ **同步普通返回** - 支持传统的一次性JSON响应
- ✅ **请求验证** - 严格按照易事厅接口规范验证请求格式
- ✅ **错误处理** - 完善的错误处理和日志记录
- ✅ **文档召回** - 模拟知识库文档召回功能
- ✅ **健康检查** - 提供服务状态检查接口

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python server.py
```

服务将在 `http://localhost:8080` 启动。

### 3. 运行测试

```bash
python test_client.py
```

## 📋 API接口说明

### 健康检查

```
GET /health
```

返回服务状态信息。

### 流式聊天接口（推荐）

```
POST /chat
```

支持同步流式返回，符合易事厅智能机器人要求。

**请求格式：**
```json
{
  "user": "用户名",
  "msg_type": "text",
  "content": "用户消息内容",
  "msg_id": "消息ID",
  "session_id": "会话ID",
  "business_keys": ["业务标识"]
}
```

**响应格式（SSE流）：**
```
event:delta
data:{"response": "流", "finished": false, "global_output": {"urls":"", "context":"", "answer_success":0, "docs":[]}}

event:delta  
data:{"response": "式", "finished": false, "global_output": {"urls":"", "context":"", "answer_success":0, "docs":[]}}

event:delta
data:{"response": "回", "finished": false, "global_output": {"urls":"", "context":"", "answer_success":0, "docs":[]}}

event:delta
data:{"response": "答", "finished": true, "global_output": {"answer_success":1, "docs":[{"doc_id":"4010230492", "title":"易事厅使用指南", "url":"http://iwiki.woa.com/p/4010230492"}]}}
```

### 同步聊天接口

```
POST /chat/sync
```

传统的一次性JSON响应，用于对比测试。

**响应格式：**
```json
{
  "code": 0,
  "err_msg": "",
  "is_async_response": false,
  "is_recall_success": 1,
  "recall_docs": [
    {
      "doc_id": "4010230492",
      "space_id": "632685097",
      "title": "易事厅使用指南", 
      "url": "http://iwiki.woa.com/p/4010230492",
      "score": 0.881664
    }
  ],
  "msg_type": "text",
  "msg_content": "机器人回复内容",
  "third_party_trace_id": "追踪ID"
}
```

## 🧪 测试指南

### 使用curl测试流式接口

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "msg_type": "text",
    "content": "你好",
    "msg_id": "test_123",
    "session_id": "session_456"
  }' \
  --no-buffer
```

### 使用curl测试同步接口

```bash
curl -X POST http://localhost:8080/chat/sync \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user", 
    "msg_type": "text",
    "content": "你好"
  }'
```

### 使用Python测试

运行提供的测试脚本：

```bash
python test_client.py
```

## 🔧 配置说明

### 服务器配置

在 `server.py` 中可以修改以下配置：

- **端口**: 默认 8080，可在 `app.run()` 中修改
- **主机**: 默认 `0.0.0.0`，允许外部访问
- **调试模式**: 默认开启，生产环境建议关闭

### 机器人配置

在 `ChatBot` 类中可以自定义：

- **回复逻辑**: 修改 `generate_response()` 方法
- **流式延迟**: 调整 `stream_response()` 中的 `time.sleep()` 
- **文档库**: 修改 `mock_docs` 列表

## 📝 易事厅接入配置

### 1. 申请接入

按照易事厅指南申请第三方机器人API接入。

### 2. 配置回调地址

在易事厅后台配置您的API地址：

- **流式接口（智能机器人）**: `http://your-domain:8080/chat`
- **同步接口（客服号/群机器人）**: `http://your-domain:8080/chat/sync`

### 3. 配置要点

- ✅ 客服号、群机器人问答只支持同步问答接口 (`/chat/sync`)
- ✅ 智能机器人问答只支持流式问答接口 (`/chat`)
- ✅ 超时时间：60秒（不可配置）
- ✅ 错误处理：status code 非200或err_msg非空视为失败

## 🔍 日志和监控

### 日志级别

默认INFO级别，包含：
- 请求接收日志
- 用户消息日志  
- 错误异常日志

### 性能监控

- 响应时间：流式每字符约50ms延迟
- 并发处理：支持多线程处理
- 健康检查：`GET /health` 监控服务状态

## 🛠️ 扩展开发

### 集成真实LLM

替换 `ChatBot.generate_response()` 方法：

```python
def generate_response(self, user_input: str) -> str:
    # 调用您的LLM API
    response = your_llm_api.chat(user_input)
    return response
```

### 集成知识库

替换 `mock_docs` 为真实文档检索：

```python
def get_relevant_docs(self, query: str):
    # 调用您的知识库检索API
    docs = your_kb_api.search(query)
    return docs
```

### 异步支持

虽然易事厅暂不支持异步返回，但您可以预先实现：

```python
@app.route('/chat/async', methods=['POST'])
def chat_async():
    # 返回异步响应
    return jsonify({
        "code": 0,
        "err_msg": "",
        "is_async_response": True,
        "third_party_trace_id": trace_id
    })
    
    # 后续通过OpenAPI发送消息
```

## 📚 参考资料

- [易事厅第三方机器人API接入指南](原文档链接)
- [企业微信客服号消息协议](https://km.woa.com/group/34327/articles/show/334049)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [Server-Sent Events规范](https://developer.mozilla.org/zh-CN/docs/Web/API/Server-sent_events)

## ❓ 常见问题

### Q: 为什么流式返回会逐字符输出？
A: 这是为了模拟真实的AI对话体验，您可以根据需要调整分割粒度。

### Q: 如何处理超长响应？
A: 注意60秒超时限制，建议控制回复长度或优化响应速度。

### Q: 如何处理并发请求？
A: Flask默认支持多线程，大量并发建议使用gunicorn等WSGI服务器。

### Q: 如何部署到生产环境？
A: 建议使用nginx + gunicorn + supervisor的部署方案。

## 📄 许可证

本项目基于MIT许可证开源。 