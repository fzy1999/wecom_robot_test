#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信复读机器人启动脚本
"""

import sys
import os
from wecom_config import WeComConfig

def main():
    """主函数"""
    config_manager = WeComConfig()
    
    # 检查配置
    if not config_manager.is_configured():
        print("⚠️  机器人尚未配置，启动配置向导...")
        if not config_manager.setup_interactive():
            print("❌ 配置失败，请重新运行配置向导")
            return
    
    # 获取配置
    token = config_manager.get_token()
    encoding_aes_key = config_manager.get_encoding_aes_key()
    server_config = config_manager.get_server_config()
    
    # 更新机器人配置
    try:
        from wecom_robot import BOT_CONFIG, app
        BOT_CONFIG['token'] = token
        BOT_CONFIG['encoding_aes_key'] = encoding_aes_key
        
        # 重新初始化机器人
        from wecom_robot import WeComRepeaterBot
        global bot
        bot = WeComRepeaterBot(token, encoding_aes_key)
        
        print("=" * 60)
        print("🤖 企业微信群机器人复读机启动中...")
        print("=" * 60)
        print(f"📍 回调地址: http://{server_config['host']}:{server_config['port']}/wecom/callback")
        print(f"🌐 健康检查: http://{server_config['host']}:{server_config['port']}/health")
        print(f"⚙️  配置管理: http://{server_config['host']}:{server_config['port']}/config")
        print("=" * 60)
        print("✅ 机器人已启动，等待消息...")
        
        # 启动Flask应用
        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug']
        )
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装所有依赖包: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 