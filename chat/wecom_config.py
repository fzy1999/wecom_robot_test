#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信机器人配置管理
"""

import os
import json

class WeComConfig:
    """企业微信机器人配置管理"""
    
    def __init__(self, config_file="wecom_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.default_config()
        else:
            return self.default_config()
    
    def default_config(self):
        """默认配置"""
        return {
            "token": "",
            "encoding_aes_key": "",
            "server": {
                "host": "0.0.0.0",
                "port": 7070,
                "debug": False
            },
            "callback_url": "/wecom/callback",
            "features": {
                "enable_image_tips": True,
                "enable_event_responses": True,
                "enable_mixed_text_extract": True
            }
        }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def set_token(self, token):
        """设置Token"""
        self.config["token"] = token
        return self.save_config()
    
    def set_encoding_aes_key(self, key):
        """设置EncodingAESKey"""
        self.config["encoding_aes_key"] = key
        return self.save_config()
    
    def get_token(self):
        """获取Token"""
        return self.config.get("token", "")
    
    def get_encoding_aes_key(self):
        """获取EncodingAESKey"""
        return self.config.get("encoding_aes_key", "")
    
    def get_server_config(self):
        """获取服务器配置"""
        return self.config.get("server", self.default_config()["server"])
    
    def is_configured(self):
        """检查是否已配置"""
        return bool(self.get_token() and self.get_encoding_aes_key())
    
    def setup_interactive(self):
        """交互式配置"""
        print("=" * 60)
        print("🤖 企业微信机器人配置向导")
        print("=" * 60)
        
        print("\n请按照以下步骤配置机器人:")
        print("1. 在企业微信管理后台创建群机器人")
        print("2. 获取Token和EncodingAESKey")
        print("3. 设置回调URL")
        
        # 配置Token
        current_token = self.get_token()
        if current_token:
            print(f"\n当前Token: {current_token[:10]}...")
            if input("是否要修改Token? (y/N): ").lower() == 'y':
                token = input("请输入新的Token: ").strip()
                if token:
                    self.set_token(token)
        else:
            token = input("\n请输入Token: ").strip()
            if token:
                self.set_token(token)
        
        # 配置EncodingAESKey
        current_key = self.get_encoding_aes_key()
        if current_key:
            print(f"\n当前EncodingAESKey: {current_key[:10]}...")
            if input("是否要修改EncodingAESKey? (y/N): ").lower() == 'y':
                key = input("请输入新的EncodingAESKey: ").strip()
                if key:
                    self.set_encoding_aes_key(key)
        else:
            key = input("\n请输入EncodingAESKey: ").strip()
            if key:
                self.set_encoding_aes_key(key)
        
        # 显示回调URL信息
        server_config = self.get_server_config()
        callback_url = f"http://你的域名或IP:{server_config['port']}{self.config['callback_url']}"
        print(f"\n📍 请在企业微信机器人配置页面设置以下回调URL:")
        print(f"   {callback_url}")
        print("\n⚠️  注意事项:")
        print("   1. 确保服务器能被企业微信访问到")
        print("   2. 如果使用HTTPS，请确保证书有效")
        print("   3. 回调URL必须能正常响应GET和POST请求")
        
        if self.is_configured():
            print("\n✅ 配置完成！可以启动机器人了。")
        else:
            print("\n❌ 配置不完整，请确保Token和EncodingAESKey都已设置。")
        
        return self.is_configured()

if __name__ == "__main__":
    config = WeComConfig()
    config.setup_interactive() 