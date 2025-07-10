#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易事厅机器人API测试客户端
用于测试同步流式返回和普通同步返回功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:9090"

def test_health():
    """测试健康检查接口"""
    print("=" * 50)
    print("🔍 测试健康检查接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    print()

def test_sync_chat():
    """测试同步聊天接口（非流式）"""
    print("=" * 50)
    print("💬 测试同步聊天接口（非流式）...")
    
    test_data = {
        "user": "test_user",
        "msg_type": "text",
        "content": "你好，机器人",
        "msg_id": "msg_123",
        "session_id": "session_456",
        "business_keys": ["test_key"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/sync",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 同步聊天测试失败: {e}")
    print()

def test_stream_chat():
    """测试流式聊天接口"""
    print("=" * 50)
    print("🔄 测试流式聊天接口...")
    
    test_data = {
        "user": "test_user",
        "msg_type": "text", 
        "content": "测试流式返回",
        "msg_id": "msg_789",
        "session_id": "session_101",
        "business_keys": ["test_key"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=test_data,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"状态码: {response.status_code}")
        print("流式响应内容:")
        print("-" * 30)
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                print(line_str)
                
                # 解析SSE数据
                if line_str.startswith('data:'):
                    try:
                        data_json = json.loads(line_str[5:])  # 去掉 'data:' 前缀
                        full_response += data_json.get('response', '')
                        
                        if data_json.get('finished'):
                            print(f"\n✅ 流式响应完成")
                            print(f"完整回答: {full_response}")
                            docs = data_json.get('global_output', {}).get('docs', [])
                            if docs:
                                print(f"召回文档数量: {len(docs)}")
                            break
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON解析错误: {e}")
                        
    except Exception as e:
        print(f"❌ 流式聊天测试失败: {e}")
    print()

def test_different_inputs():
    """测试不同的输入内容"""
    print("=" * 50)
    print("🧪 测试不同输入内容的流式响应...")
    
    test_cases = [
        "你好",
        "机器人功能介绍", 
        "如何配置机器人",
        "这是一个测试消息"
    ]
    
    for i, content in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {content}")
        print("-" * 20)
        
        test_data = {
            "user": f"test_user_{i}",
            "msg_type": "text",
            "content": content,
            "msg_id": f"msg_{i}",
            "session_id": f"session_{i}",
            "business_keys": ["test_key"]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json=test_data,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data:'):
                        try:
                            data_json = json.loads(line_str[5:])
                            full_response += data_json.get('response', '')
                            if data_json.get('finished'):
                                print(f"回答: {full_response}")
                                break
                        except json.JSONDecodeError:
                            pass
                            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        time.sleep(1)  # 间隔1秒

def main():
    """主测试函数"""
    print("🚀 开始测试易事厅机器人API...")
    print(f"API地址: {BASE_URL}")
    print()
    
    # 测试健康检查
    test_health()
    
    # 测试同步接口
    test_sync_chat()
    
    # 测试流式接口
    test_stream_chat()
    
    # 测试不同输入
    test_different_inputs()
    
    print("=" * 50)
    print("✅ 所有测试完成!")

if __name__ == "__main__":
    main() 