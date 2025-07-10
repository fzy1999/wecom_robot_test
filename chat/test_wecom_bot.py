#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信复读机器人测试脚本
"""

import requests
import json
import time

def test_health_check(base_url="http://localhost:8080"):
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 健康检查成功: {result}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_config_interface(base_url="http://localhost:8080"):
    """测试配置接口"""
    print("\n🔍 测试配置接口...")
    try:
        # 获取配置
        response = requests.get(f"{base_url}/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 配置获取成功: {config}")
            return True
        else:
            print(f"❌ 配置获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 配置接口异常: {e}")
        return False

def simulate_url_verification(base_url="http://localhost:8080"):
    """模拟URL验证请求"""
    print("\n🔍 模拟URL验证...")
    
    # 模拟企业微信的URL验证参数
    params = {
        'msg_signature': 'test_signature',
        'timestamp': str(int(time.time())),
        'nonce': 'test_nonce',
        'echostr': 'test_echostr'
    }
    
    try:
        response = requests.get(f"{base_url}/wecom/callback", params=params, timeout=5)
        print(f"📝 URL验证响应: status={response.status_code}, content={response.text[:100]}")
        
        # 403是预期的，因为我们没有正确的签名
        if response.status_code in [200, 403]:
            print("✅ URL验证接口正常响应")
            return True
        else:
            print(f"❌ URL验证异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ URL验证异常: {e}")
        return False

def simulate_message_callback(base_url="http://localhost:8080"):
    """模拟消息回调请求"""
    print("\n🔍 模拟消息回调...")
    
    # 模拟加密的消息回调
    xml_data = """<xml>
<Encrypt><![CDATA[test_encrypted_message]]></Encrypt>
</xml>"""
    
    params = {
        'msg_signature': 'test_signature',
        'timestamp': str(int(time.time())),
        'nonce': 'test_nonce'
    }
    
    try:
        response = requests.post(
            f"{base_url}/wecom/callback",
            params=params,
            data=xml_data,
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        
        print(f"📝 消息回调响应: status={response.status_code}, content={response.text[:100]}")
        
        # 200是预期的，即使解密失败也会返回200
        if response.status_code == 200:
            print("✅ 消息回调接口正常响应")
            return True
        else:
            print(f"❌ 消息回调异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 消息回调异常: {e}")
        return False

def test_server_connectivity(host="localhost", port=8080):
    """测试服务器连通性"""
    print(f"\n🔍 测试服务器连通性 {host}:{port}...")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ 服务器连通性正常: {host}:{port}")
            return True
        else:
            print(f"❌ 服务器连接失败: {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ 连通性测试异常: {e}")
        return False

def run_all_tests(base_url="http://localhost:8080"):
    """运行所有测试"""
    print("=" * 60)
    print("🧪 企业微信复读机器人测试")
    print("=" * 60)
    
    # 解析URL获取host和port
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 8080
    
    results = []
    
    # 测试服务器连通性
    results.append(test_server_connectivity(host, port))
    
    # 如果服务器连通，继续其他测试
    if results[-1]:
        results.append(test_health_check(base_url))
        results.append(test_config_interface(base_url))
        results.append(simulate_url_verification(base_url))
        results.append(simulate_message_callback(base_url))
    
    # 测试结果统计
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total-passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！机器人服务正常运行。")
    else:
        print("\n⚠️  部分测试失败，请检查服务器状态和配置。")
    
    return passed == total

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='企业微信复读机器人测试工具')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='机器人服务地址 (默认: http://localhost:8080)')
    parser.add_argument('--host', default='localhost', 
                       help='服务器主机 (默认: localhost)')
    parser.add_argument('--port', type=int, default=8080, 
                       help='服务器端口 (默认: 8080)')
    
    args = parser.parse_args()
    
    # 如果指定了host和port，构造base_url
    if args.host != 'localhost' or args.port != 8080:
        base_url = f"http://{args.host}:{args.port}"
    else:
        base_url = args.url
    
    success = run_all_tests(base_url)
    
    if success:
        print("\n🔧 接下来可以:")
        print("1. 在企业微信后台配置回调URL")
        print("2. 将机器人添加到群聊进行测试")
        print("3. 发送消息验证复读功能")
    else:
        print("\n🔧 建议:")
        print("1. 检查机器人服务是否正常启动")
        print("2. 确认服务端口没有被占用")
        print("3. 检查防火墙和网络配置")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 