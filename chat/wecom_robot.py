#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信群机器人复读机
功能：用户向机器人发什么，机器人就返回什么
"""

import json
import time
import base64
import hashlib
import logging
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, unquote
from flask import Flask, request, Response
try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        print("请安装 pycryptodome: pip install pycryptodome")
        exit(1)
import struct
import socket
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WXBizMsgCrypt:
    """企业微信消息加解密类"""
    
    def __init__(self, token, encoding_aes_key, receiveid):
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.receiveid = receiveid
        
        # Base64解码AES密钥 - 修复padding问题
        self.aes_key = self._decode_aes_key(encoding_aes_key)
    
    def _decode_aes_key(self, encoding_aes_key):
        """安全解码AES密钥，处理padding问题"""
        try:
            # 企业微信的EncodingAESKey是43位，标准Base64编码
            # 首先尝试直接解码
            return base64.b64decode(encoding_aes_key)
        except Exception as e1:
            try:
                # 如果失败，尝试添加适当的padding
                missing_padding = len(encoding_aes_key) % 4
                if missing_padding:
                    encoding_aes_key += '=' * (4 - missing_padding)
                return base64.b64decode(encoding_aes_key)
            except Exception as e2:
                logger.error(f"AES密钥解码失败: 原始错误={e1}, 填充后错误={e2}")
                logger.error(f"EncodingAESKey长度: {len(encoding_aes_key)}, 内容前10位: {encoding_aes_key[:10]}...")
                raise ValueError(f"无效的EncodingAESKey格式: {e2}")
        
    def _get_sha1(self, token, timestamp, nonce, encrypt):
        """计算签名"""
        sortlist = [token, timestamp, nonce, encrypt]
        sortlist.sort()
        sha = hashlib.sha1()
        sha.update("".join(sortlist).encode('utf-8'))
        return sha.hexdigest()
    
    def _decrypt(self, text, receiveid):
        """解密消息"""
        try:
            cryptor = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            plain_text = cryptor.decrypt(base64.b64decode(text))
            
            # 去除补位字符
            pad = plain_text[-1]
            if isinstance(pad, str):
                pad = ord(pad)
            content = plain_text[16:-pad]
            
            # 提取消息长度
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4:xml_len+4].decode('utf-8')
            from_receiveid = content[xml_len+4:].decode('utf-8')
            
            return 0, xml_content
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return -40007, None
    
    def _encrypt(self, text, receiveid):
        """加密消息"""
        try:
            # 16位随机字符串
            random_str = self._get_random_str()
            
            # 消息长度
            text_bytes = text.encode('utf-8')
            text_len = len(text_bytes)
            
            # 拼接
            msg = random_str.encode('utf-8') + struct.pack("I", socket.htonl(text_len)) + text_bytes + receiveid.encode('utf-8')
            
            # PKCS7 padding
            block_size = 32
            amount_to_pad = block_size - (len(msg) % block_size)
            if amount_to_pad == 0:
                amount_to_pad = block_size
            pad = chr(amount_to_pad).encode('utf-8')
            msg = msg + pad * amount_to_pad
            
            # 加密
            cryptor = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            encrypted = cryptor.encrypt(msg)
            
            return 0, base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"加密失败: {e}")
            return -40006, None
    
    def _get_random_str(self):
        """生成16位随机字符串"""
        import random
        import string
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    def verify_url(self, msg_signature, timestamp, nonce, echostr):
        """验证URL有效性"""
        sha1 = self._get_sha1(self.token, timestamp, nonce, echostr)
        if sha1 == msg_signature:
            ret, reply_echostr = self._decrypt(echostr, self.receiveid)
            return ret, reply_echostr
        else:
            return -40001, None
    
    def decrypt_msg(self, msg_signature, timestamp, nonce, post_data):
        """解密消息"""
        # 解析XML
        try:
            root = ET.fromstring(post_data)
            encrypt_element = root.find('Encrypt')
            if encrypt_element is None or encrypt_element.text is None:
                logger.error("XML中没有找到Encrypt元素或其内容为空")
                return -40002, None
            encrypt = encrypt_element.text
        except Exception as e:
            logger.error(f"解析XML失败: {e}")
            return -40002, None
        
        # 验证签名
        sha1 = self._get_sha1(self.token, timestamp, nonce, encrypt)
        if sha1 != msg_signature:
            return -40001, None
        
        # 解密
        return self._decrypt(encrypt, self.receiveid)
    
    def encrypt_msg(self, reply_msg, nonce, timestamp=None):
        """加密回复消息"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        # 加密消息
        ret, encrypt = self._encrypt(reply_msg, self.receiveid)
        if ret != 0:
            return ret, None
        
        # 生成签名
        signature = self._get_sha1(self.token, timestamp, nonce, encrypt)
        
        # 构造回复XML
        resp_dict = {
            'Encrypt': encrypt,
            'MsgSignature': signature,
            'TimeStamp': timestamp,
            'Nonce': nonce
        }
        
        resp_xml = f"""<xml>
<Encrypt><![CDATA[{encrypt}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        
        return 0, resp_xml

class WeComRepeaterBot:
    """企业微信复读机器人"""
    
    def __init__(self, token, encoding_aes_key):
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.receiveid = ""  # 群机器人场景下为空字符串
        self.wxcrypt = WXBizMsgCrypt(token, encoding_aes_key, self.receiveid)
        # 存储已处理的消息ID，用于去重
        self.processed_msgs = set()
    
    def verify_url(self, args):
        """验证URL有效性"""
        msg_signature = args.get('msg_signature', '')
        timestamp = args.get('timestamp', '')
        nonce = args.get('nonce', '')
        echostr = args.get('echostr', '')
        
        logger.info(f"URL验证请求: signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
        
        ret, reply_echostr = self.wxcrypt.verify_url(msg_signature, timestamp, nonce, echostr)
        if ret == 0:
            logger.info("URL验证成功")
            return reply_echostr
        else:
            logger.error(f"URL验证失败: {ret}")
            return None
    
    def process_message(self, args, post_data):
        """处理回调消息"""
        msg_signature = args.get('msg_signature', '')
        timestamp = args.get('timestamp', '')
        nonce = args.get('nonce', '')
        
        logger.info(f"收到消息回调: signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
        
        # 解密消息
        ret, xml_content = self.wxcrypt.decrypt_msg(msg_signature, timestamp, nonce, post_data)
        if ret != 0:
            logger.error(f"消息解密失败: {ret}")
            return ""
        
        logger.info(f"解密后的消息: {xml_content}")
        
        # 解析消息
        try:
            root = ET.fromstring(xml_content)
            msg_type = root.find('MsgType').text
            msg_id = root.find('MsgId').text if root.find('MsgId') is not None else ""
            webhook_url = root.find('WebhookUrl').text if root.find('WebhookUrl') is not None else ""
            
            # 消息去重
            if msg_id and msg_id in self.processed_msgs:
                logger.info(f"消息已处理过，跳过: {msg_id}")
                return ""
            
            if msg_id:
                self.processed_msgs.add(msg_id)
                # 限制缓存大小，避免内存泄漏
                if len(self.processed_msgs) > 1000:
                    # 移除最旧的一半消息ID
                    old_msgs = list(self.processed_msgs)[:500]
                    for old_msg in old_msgs:
                        self.processed_msgs.discard(old_msg)
            
            # 根据消息类型处理
            reply_msg = None
            
            if msg_type == 'text':
                # 文本消息
                content = root.find('Text/Content').text
                logger.info(f"收到文本消息: {content}")
                
                # 构造回复消息
                reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{content}]]></Content>
</Text>
</xml>"""
            
            elif msg_type == 'image':
                # 图片消息 - 回复提示信息
                image_url = root.find('Image/ImageUrl').text if root.find('Image/ImageUrl') is not None else ""
                logger.info(f"收到图片消息: {image_url}")
                
                reply_content = "收到图片消息，但复读机暂不支持回复图片，只能回复文字哦~"
                reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{reply_content}]]></Content>
</Text>
</xml>"""
            
            elif msg_type == 'mixed':
                # 图文混排消息 - 提取文字部分
                logger.info("收到图文混排消息")
                text_contents = []
                
                msg_items = root.findall('MixedMessage/MsgItem')
                for item in msg_items:
                    item_type = item.find('MsgType').text
                    if item_type == 'text':
                        text_content = item.find('Text/Content').text
                        text_contents.append(text_content)
                
                if text_contents:
                    combined_content = ''.join(text_contents)
                    reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{combined_content}]]></Content>
</Text>
</xml>"""
                else:
                    reply_content = "收到图文混排消息，但其中没有文字内容可以复读~"
                    reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{reply_content}]]></Content>
</Text>
</xml>"""
            
            elif msg_type == 'event':
                # 事件消息
                event_type = root.find('Event/EventType').text if root.find('Event/EventType') is not None else ""
                logger.info(f"收到事件消息: {event_type}")
                
                if event_type == 'add_to_chat':
                    reply_content = "大家好！我是复读机器人，你们说什么我就说什么~"
                elif event_type == 'enter_chat':
                    reply_content = "欢迎来到复读机器人！发送任何文字消息，我都会原样复读给你~"
                else:
                    reply_content = f"收到事件: {event_type}"
                
                reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{reply_content}]]></Content>
</Text>
</xml>"""
            
            elif msg_type == 'attachment':
                # 按钮点击事件
                logger.info("收到按钮点击事件")
                reply_content = "收到按钮点击事件~"
                reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{reply_content}]]></Content>
</Text>
</xml>"""
            
            else:
                logger.warning(f"未知消息类型: {msg_type}")
                reply_content = f"收到未知类型消息: {msg_type}"
                reply_msg = f"""<xml>
<MsgType>text</MsgType>
<Text>
<Content><![CDATA[{reply_content}]]></Content>
</Text>
</xml>"""
            
            # 加密回复消息
            if reply_msg:
                ret, encrypted_reply = self.wxcrypt.encrypt_msg(reply_msg, nonce, timestamp)
                if ret == 0:
                    logger.info("消息处理成功，返回加密回复")
                    return encrypted_reply
                else:
                    logger.error(f"加密回复消息失败: {ret}")
                    return ""
            else:
                return ""
                
        except Exception as e:
            logger.error(f"处理消息时发生异常: {e}")
            return ""

# 配置信息 - 需要根据实际情况修改
BOT_CONFIG = {
    'token': 'your_token_here',  # 在机器人配置页面设置的Token
    'encoding_aes_key': 'your_encoding_aes_key_here'  # 在机器人配置页面设置的EncodingAESKey
}

# 初始化机器人
bot = WeComRepeaterBot(BOT_CONFIG['token'], BOT_CONFIG['encoding_aes_key'])

@app.route('/wecom/callback', methods=['GET', 'POST'])
def wecom_callback():
    """企业微信机器人回调接口"""
    try:
        # URL decode 处理
        args = {}
        for key, value in request.args.items():
            args[key] = unquote(value)
        
        if request.method == 'GET':
            # URL验证
            logger.info("收到URL验证请求")
            reply = bot.verify_url(args)
            if reply:
                return reply
            else:
                return "验证失败", 403
        
        elif request.method == 'POST':
            # 消息回调
            post_data = request.get_data().decode('utf-8')
            logger.info(f"收到POST数据: {post_data}")
            
            reply = bot.process_message(args, post_data)
            if reply:
                return reply, 200, {'Content-Type': 'application/xml'}
            else:
                return "", 200
    
    except Exception as e:
        logger.error(f"回调处理异常: {e}")
        return "服务器错误", 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "企业微信复读机器人",
        "version": "1.0.0"
    }

@app.route('/config', methods=['GET', 'POST'])
def config():
    """配置管理接口"""
    if request.method == 'GET':
        # 返回当前配置（隐藏敏感信息）
        return {
            "token": "***" if BOT_CONFIG['token'] != 'your_token_here' else BOT_CONFIG['token'],
            "encoding_aes_key": "***" if BOT_CONFIG['encoding_aes_key'] != 'your_encoding_aes_key_here' else BOT_CONFIG['encoding_aes_key']
        }
    
    elif request.method == 'POST':
        # 更新配置
        data = request.get_json()
        if 'token' in data:
            BOT_CONFIG['token'] = data['token']
        if 'encoding_aes_key' in data:
            BOT_CONFIG['encoding_aes_key'] = data['encoding_aes_key']
        
        # 重新初始化机器人
        global bot
        bot = WeComRepeaterBot(BOT_CONFIG['token'], BOT_CONFIG['encoding_aes_key'])
        
        return {"message": "配置更新成功"}

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 企业微信群机器人复读机启动中...")
    print("📋 功能说明:")
    print("   - 复读机：用户发什么，机器人就返回什么")
    print("   - 支持文本消息复读")
    print("   - 支持图文混排消息的文字部分复读")
    print("   - 回调地址: /wecom/callback")
    print("   - 健康检查: /health")
    print("   - 配置管理: /config")
    print("⚠️  请确保已正确配置Token和EncodingAESKey")
    print("=" * 60)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    ) 