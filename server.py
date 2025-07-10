#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易事厅第三方机器人API - 支持同步流式返回
基于易事厅机器人接入指南实现
"""

import json
import time
import logging
from flask import Flask, request, Response, jsonify
from typing import Dict, Any, Generator
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ChatBot:
    """模拟聊天机器人"""
    
    def __init__(self):
        # 模拟知识库文档
        self.mock_docs = [
            {
                "doc_id": "4010230492",
                "space_id": "632685097", 
                "title": "易事厅使用指南",
                "url": "http://iwiki.woa.com/p/4010230492",
                "score": 0.881664
            },
            {
                "doc_id": "4010230493",
                "space_id": "632685098",
                "title": "机器人配置说明", 
                "url": "http://iwiki.woa.com/p/4010230493",
                "score": 0.765432
            }
        ]
    
    def generate_response(self, user_input: str) -> str:
        """根据用户输入生成回答"""
        if "你好" in user_input or "hello" in user_input.lower():
            return "您好！我是易事厅智能助手，很高兴为您服务。请问有什么可以帮助您的吗？"
        elif "机器人" in user_input:
            return "关于机器人功能，我可以为您提供详细的使用指导和配置说明。您想了解哪个方面的内容呢？"
        elif "配置" in user_input:
            return "机器人配置包括接口地址设置、消息格式配置、流式返回设置等。具体配置步骤请参考相关文档。"
        elif "测试" in user_input:
            return "这是一个测试回复。机器人正在正常工作，支持同步流式返回。您可以继续测试其他功能。"
        else:
            return f"您提到了：{user_input}。我正在为您查找相关信息，请稍等片刻..."
    
    def stream_response(self, response_text: str, include_docs: bool = True) -> Generator[str, None, None]:
        """流式返回响应"""
        # 将响应文本分割成字符流
        chars = list(response_text)
        
        # 逐字符返回
        for i, char in enumerate(chars):
            is_finished = (i == len(chars) - 1)
            
            if is_finished:
                # 最后一个字符，包含召回文档信息
                data = {
                    "response": char,
                    "finished": True,
                    "global_output": {
                        "answer_success": 1 if include_docs else 0,
                        "docs": self.mock_docs if include_docs else []
                    }
                }
            else:
                # 中间字符
                data = {
                    "response": char, 
                    "finished": False,
                    "global_output": {
                        "urls": "",
                        "context": "",
                        "answer_success": 0,
                        "docs": []
                    }
                }
            
            # 构造SSE格式
            sse_data = f"event:delta\ndata:{json.dumps(data, ensure_ascii=False)}\n\n"
            yield sse_data
            
            # 模拟打字延迟
            time.sleep(0.05)

# 初始化聊天机器人
chatbot = ChatBot()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "易事厅第三方机器人API",
        "version": "1.0.0"
    })

@app.route('/chat', methods=['POST'])
def chat_stream():
    """
    主要的聊天接口 - 支持同步流式返回
    按照易事厅机器人接入指南实现
    """
    try:
        # 解析请求体
        if not request.is_json:
            logger.error("请求不是JSON格式")
            return jsonify({
                "code": 1,
                "err_msg": "请求格式错误，需要JSON格式"
            }), 400
        
        req_data = request.get_json()
        logger.info(f"收到请求: {json.dumps(req_data, ensure_ascii=False)}")
        
        # 验证必要字段
        required_fields = ['user', 'msg_type', 'content']
        for field in required_fields:
            if field not in req_data:
                logger.error(f"缺少必要字段: {field}")
                return jsonify({
                    "code": 1,
                    "err_msg": f"缺少必要字段: {field}"
                }), 400
        
        # 提取请求信息
        user = req_data.get('user', '')
        msg_type = req_data.get('msg_type', 'text')
        content = req_data.get('content', '')
        msg_id = req_data.get('msg_id', '')
        raw_msg = req_data.get('raw_msg', '')
        session_id = req_data.get('session_id', '')
        business_keys = req_data.get('business_keys', [])
        
        # 生成trace_id
        trace_id = str(uuid.uuid4())
        
        logger.info(f"用户 {user} 发送消息: {content}")
        logger.info(f"req_data: {req_data}")
        
        # 目前只支持文本消息
        if msg_type != 'text':
            logger.warning(f"不支持的消息类型: {msg_type}")
            return jsonify({
                "code": 1,
                "err_msg": f"暂不支持消息类型: {msg_type}"
            }), 400
        
        # 生成机器人回答
        bot_response = chatbot.generate_response(content)
        
        # 返回流式响应
        def generate():
            yield from chatbot.stream_response(bot_response, include_docs=True)
        
        # 设置SSE响应头
        response = Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'X-Trace-ID': trace_id
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({
            "code": 1,
            "err_msg": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/chat/sync', methods=['POST'])
def chat_sync():
    """
    同步接口示例（非流式）
    用于对比和测试
    """
    try:
        if not request.is_json:
            return jsonify({
                "code": 1,
                "err_msg": "请求格式错误，需要JSON格式"
            }), 400
        
        req_data = request.get_json()
        content = req_data.get('content', '')
        
        # 生成回答
        bot_response = chatbot.generate_response(content)
        
        # 同步返回
        return jsonify({
            "code": 0,
            "err_msg": "",
            "is_async_response": False,
            "is_recall_success": 1,
            "recall_docs": chatbot.mock_docs,
            "msg_type": "text",
            "msg_content": bot_response,
            "third_party_trace_id": str(uuid.uuid4())
        })
        
    except Exception as e:
        logger.error(f"同步接口错误: {str(e)}")
        return jsonify({
            "code": 1,
            "err_msg": f"服务器内部错误: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "code": 1,
        "err_msg": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "code": 1,
        "err_msg": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 易事厅第三方机器人API 启动中...")
    print("📋 支持功能:")
    print("   - 同步流式返回 (POST /chat)")
    print("   - 同步普通返回 (POST /chat/sync)")
    print("   - 健康检查 (GET /health)")
    print("=" * 60)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=9090,
        debug=True,
        threaded=True
    )
