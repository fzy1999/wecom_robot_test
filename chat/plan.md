企业内部开发
快速入门
服务端API
客户端API
工具与资源
附录
更新日志
联系我们

基础

连接微信

办公
企业内部开发
服务端API
消息推送
群机器人
群机器人回调说明（内测）
群机器人回调说明（内测）
最后更新：2024/10/11
概述
创建或编辑机器人时，可以设置回调url，用于接收消息或者事件。
以下几种情况会回调：
1.用户群里@机器人或者单聊中向机器人发送文本消息或图文混排消息，该条消息会加密回调到设置的url
2.群机器人被添加到其他群
3.群机器人从其他群被移除
4.用户进入机器人单聊界面
5.用户点击机器人markdown消息中的按钮的时候会回调
6.用户在单聊界面中给机器人发送图片消息
7.用户在小黑板中@机器人

 

回调加密方案
与应用的回调加密方案基本一致，有关键的三个步骤：验证URL有效性、接收与解密、加密与回复。开发者可以直接使用企业微信为应用提供的加解密库（目前已有c++/python/php/java/c#等语言版本），需要注意的是，加解密库要求传 receiveid 参数， 在群机器人的使用场景里，receiveid直接传空字符串即可。

设置接收消息的参数
在群机器人的配置页面设置接收消息的参数。
要求填写群机器人的URL、Token、EncodingAESKey三个参数

URL是群机器人接收企业微信群推送请求的访问协议和地址，支持http或https协议。
Token可由开发者任意填写，用于生成签名。长度为3~32之间的英文或数字.
EncodingAESKey用于消息体的加密，是AES密钥的Base64编码。 长度为43位的英文或数字。
这三个参数的用处在加解密方案说明会详细介绍，此处可不用细究。

验证URL有效性
当点击“保存”提交以上信息时，企业微信会发送一条验证消息到填写的URL，发送方法为GET。
群机器人的接收消息服务器接收到验证请求后，需要作出正确的响应才能通过URL验证。

获取请求参数时需要做Urldecode处理，否则会验证不成功
假设接收消息地址设置为：https://api.3dept.com/，企业微信将向该地址发送如下验证请求：

请求方式：GET

请求地址：https://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323&echostr=ENCRYPT_STR
参数说明

参数	必须	说明
msg_signature	是	企业微信加密签名，msg_signature结合了开发者填写的token、请求中的timestamp、nonce参数、加密的消息体
timestamp	是	时间戳
nonce	是	随机数，两个小时内保证不重复
echostr	是	加密的字符串。需要解密得到消息内容明文，解密后有random、msg_len、msg三个字段，其中msg即为消息内容明文
机器人后台收到请求后，需要做如下操作：

对收到的请求做Urldecode处理
通过参数msg_signature对请求进行校验，确认调用者的合法性。
解密echostr参数得到消息内容(即msg字段)
在1秒内响应GET请求，响应内容为上一步得到的明文消息内容(不能加引号，不能带bom头，不能带换行符)
以上2~3步骤可以直接使用验证URL函数一步到位。
之后接入验证生效，接收消息开启成功。

接收与解密
开启接收消息模式后，企业微信会将消息发送给群机器人的回调URL，机器人后台需要做正确的响应。

接收消息的说明
企业微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共重试三次。如果开发者在调试中，发现成员无法收到被动回复的消息，可以检查是否消息处理超时。
当接收成功后，http头部返回200表示接收ok，其他错误码像302企业微信后台会一律当做失败并发起重试。
由于消息回调可能会重试机器人需要按msgid排重。
假如机器人后台无法保证在五秒内处理并回复，或者不想回复任何内容，可以直接返回200（即以空串为返回包）。机器人后台后续可以使用主动发消息接口进行异步回复。
接收密文协议
假设机器人的接收消息的URL设置为https://api.3dept.com。
请求方式：POST

请求地址 ：https://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323

接收数据格式 ：

<xml> 
   <Encrypt><![CDATA[msg_encrypt]]></Encrypt>
</xml>
参数说明

参数	说明
Encrypt	消息结构体加密后的字符串
企业收到消息后，需要作如下处理：

对msg_signature进行校验
解密Encrypt，得到明文的消息结构体，解密过程参见“密文解密得到msg的过程”，注意文档中的receiveid参数在群机器人回调场景里为空串。
解密后的消息结构体
群机器人回调消息有以下类型：

文本(text)。用户群里@机器人或者单聊中向机器人发送文本消息的时候会回调。
事件(event)。机器人被加入到群中或者从群里移除的时候回调。
附件（attachment）。用户点击markdown消息中的按钮的时候会回调。
图片（image）。用户在单聊中向机器人发送图片消息的时候会回调。
图文混排（mixed）。用户群里@机器人或者单聊中向机器人发送图文混排消息的时候会回调。
命令（command）。用户在小黑板里发出特定命令给机器人后产生回调。
Encrypt解密后是xml格式的明文消息结构体。

文本消息
xml协议格式如下：

<xml>
	<WebhookUrl> <![CDATA[http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK]]></WebhookUrl>
	<MsgId>abcdabcdabcd</MsgId>
	<ChatId><![CDATA[wrkSFfCgAALFgnrSsWU38puiv4yvExuw]]></ChatId>
	<PostId><![CDATA[bpkSFfCgAAWeiHos2p6lJbG3_F2xxxxx]]></PostId>
	<ChatType>single</ChatType>
	<From>
		<UserId>zhangsan</UserId>
		<Name><![CDATA[张三]]></Name>
		<Alias><![CDATA[jackzhang]]></Alias>
	</From>
	<GetChatInfoUrl><![CDATA[https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE]]></GetChatInfoUrl>
	<MsgType>text</MsgType>
	<Text>
		<Content><![CDATA[@RobotA hello robot]]></Content>
	</Text>
</xml>
xml协议参数说明：

参数	说明
WebhookUrl	机器人主动推送消息的url
MsgId	消息Id，可用于去重
ChatId	会话id，可能是群聊，也可能是单聊，也可能是小黑板
PostId	小黑板帖子id，当前消息为小黑板回帖消息时带上
ChatType	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
From	该消息发送者的信息
From.UserId	发送者的userid
From.Name	发送者姓名
From.Alias	发送者别名
GetChatInfoUrl	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
MsgType	消息类型，此时固定是text
Text.Content	消息内容
json协议格式如下：

{
    "webhook_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK",
	"msgid":"CAIQ16HMjQYY\/NGagIOAgAMgq4KM0AI=",
    "chatid":"CHATID",
    "postid":"POSTID",
    "chattype":"group",
    "from":{
        "userid":"zhangsan",
        "name":"张三",
        "alias":"jackzhang"
    },
    "get_chat_info_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE",
    "msgtype":"text",
    "text":{
        "content":"@RobotA hello robot"
    }
}
json协议参数说明：

参数	说明
webhook_url	机器人主动推送消息的url
msgid	消息Id，可用于去重
chatid	会话id，可能是群聊，也可能是单聊，也可能是小黑板
postid	小黑板帖子id，当前消息为小黑板回帖消息时带上
chattype	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
from	该消息发送者的信息
from.userId	发送者的userid
from.name	发送者姓名
from.alias	发送者别名
get_chat_info_url	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
msgtype	消息类型，此时固定是text
text.content	消息内容
 

图片消息
注意：目前仅单聊支持回调图片消息
xml协议格式如下：

<xml>
	<WebhookUrl> <![CDATA[https://qyapi.weixin.qq.com/xxxxxxx]]></WebhookUrl>
	<ChatId><![CDATA[wrkSFfCgAALFgnrSsWU38puiv4yvExuw]]></ChatId>
	<ChatType>single</ChatType>
	<From>
		<UserId>zhangsan</UserId>
		<Name><![CDATA[张三]]></Name>
		<Alias><![CDATA[jackzhang]]></Alias>
	</From>
	<GetChatInfoUrl><![CDATA[https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE]]></GetChatInfoUrl>
	<MsgType>image</MsgType>
	<Image>
		<ImageUrl><![CDATA[https://p.qpic.cn/pic_wework/2085796/353325df3d4200754264e0521fd8f01e32a878aae7e52a/0]]></ImageUrl>
	</Image>
	<MsgId>abcdabcdabcd</MsgId>
</xml>
xml协议参数说明：

参数	说明
WebhookUrl	机器人主动推送消息的url
MsgId	消息Id，可用于去重
ChatId	会话id，可能是群聊，也可能是单聊，也可能是小黑板
PostId	小黑板帖子id，当前消息为小黑板回帖消息时带上
ChatType	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
From	该消息发送者的信息
From.UserId	发送者的userid
From.Name	发送者姓名
From.Alias	发送者别名
GetChatInfoUrl	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
MsgType	消息类型，此时固定是image
Image.Content	消息内容
 

json协议格式如下：

{
    "webhook_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK",
    "msgid":"CAIQz7/MjQYY/NGagIOAgAMgl8jK/gI=",
    "chatid":"wokSFfCgAAvBKmWMiwoJDzAJOVhg4Bbg",
    "chattype":"single",
    "from":{
        "userid":"zhangsan",
        "name":"张三",
        "alias":"jackzhang"
    },
    "get_chat_info_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE",
    "msgtype":"image",
    "image":{
        "image_url":"https://wework.qpic.cn/wwpic/886738_NUdSwFG0QtyVEdZ_1639129039/0"
    }
}
json协议参数说明：

参数	说明
webhook_url	机器人主动推送消息的url
msgid	消息Id，可用于去重
chatid	会话id，可能是群聊，也可能是单聊，也可能是小黑板
postid	小黑板帖子id，当前消息为小黑板回帖消息时带上
chattype	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
from	该消息发送者的信息
from.userId	发送者的userid
from.name	发送者姓名
from.alias	发送者别名
get_chat_info_url	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
msgtype	消息类型，此时固定是image
image.image_url	消息内容
事件消息
xml协议格式如下：

<xml>
	<WebhookUrl> <![CDATA[https://qyapi.weixin.qq.com/xxxxxxx]]></WebhookUrl>
	<ChatId><![CDATA[wrkSFfCgAALFgnrSsWU38puiv4yvExuw]]></ChatId>
	<ChatType>single</ChatType>
	<GetChatInfoUrl><![CDATA[https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=m49c5aRCdEP8_QQdZmTNR52yJ5TLGcIMzaLJk3x5KqY]]></GetChatInfoUrl>
	<From>
		<UserId>zhangsan</UserId>
		<Name><![CDATA[张三]]></Name>
		<Alias><![CDATA[jackzhang]]></Alias>
	</From>
	<MsgType>event</MsgType>
	<Event>
		<EventType><![CDATA[add_to_chat]]></EventType>
	</Event>
	<MsgId>abcdabcdabcd</MsgId>
</xml>
xml协议参数说明：

参数	说明
WebhookUrl	机器人主动推送消息的url
MsgId	消息Id，可用于去重
ChatId	会话id，可能是群聊，也可能是单聊，也可能是小黑板
PostId	小黑板帖子id，当前消息为小黑板回帖消息时带上
ChatType	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
From	该消息发送者的信息
From.UserId	发送者的userid
From.Name	发送者姓名
From.Alias	发送者别名
GetChatInfoUrl	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
MsgType	消息类型，此时固定是event
EventType	事件类型：目前可能是add_to_chat表示被添加进会话，或者delete_from_chat表示被移出会话, enter_chat 表示用户进入机器人单聊
json协议格式如下：

{
    "webhook_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK",
    "msgid":"hX7-qR-YSuKTmrMFYeLQVwAA",
    "chatid":"CHATID",
    "chattype":"single",
    "from":{
        "userid":"zhangsan",
        "name":"张三",
        "alias":"brandongbu"
    },
    "get_chat_info_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CvoJ1rXy8kMu19sA2lmWfaqDCBXMDBci2K5JEbp90l8",
    "msgtype":"event",
    "event":{
        "event_type":"enter_chat"
    }
}
json协议参数说明：

参数	说明
webhook_url	机器人主动推送消息的url
msgid	消息Id，可用于去重
chatid	会话id，可能是群聊，也可能是单聊，也可能是小黑板
postid	小黑板帖子id，当前消息为小黑板回帖消息时带上
chattype	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
from	该消息发送者的信息
from.userId	发送者的userid
from.name	发送者姓名
from.alias	发送者别名
get_chat_info_url	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
msgtype	消息类型，此时固定是event
event.event_type	事件类型：目前可能是add_to_chat表示被添加进会话，或者delete_from_chat表示被移出会话, enter_chat 表示用户进入机器人单聊
 

attachment事件消息
机器人可以通过接口发送带attachment的markdown消息，目前attachment支持按钮类型，当用户点击按钮时，企业微信往机器人回调相应的事件
xml协议格式如下：

<xml>
	<WebhookUrl><![CDATA[http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK]]></WebhookUrl>
	<MsgId><![CDATA[0GLL5fDZQF-1ygUp_4ECfAAA]]></MsgId>
	<ChatId><![CDATA[CHATID]]></ChatId>
	<PostId><![CDATA[POSTID]]></PostId>
	<ChatType>group</ChatType>
	<From>
		<UserId><![CDATA[zhangsan]]></UserId>
		<Name><![CDATA[张三]]></Name>
		<Alias><![CDATA[zhangsan]]></Alias>
	</From>
	<GetChatInfoUrl><![CDATA[https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE]]></GetChatInfoUrl>
	<MsgType><![CDATA[attachment]]></MsgType>
	<Attachment>
		<CallbackId><![CDATA[btn_for_show_more]]></CallbackId>
		<Actions>
			<Name><![CDATA[btn_more]]></Name>
			<Value><![CDATA[btn_more]]></Value>
			<Type><![CDATA[button]]></Type>
		</Actions>
	</Attachment>
</xml>
xml协议参数说明：

参数	说明
WebhookUrl	机器人主动推送消息的url
MsgId	消息Id，可用于去重
ChatId	会话id，可能是群聊，也可能是单聊，也可能是小黑板
PostId	小黑板帖子id，当前消息为小黑板回帖消息时带上
ChatType	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
From	该消息发送者的信息
From.UserId	发送者的userid
From.Name	发送者姓名
From.Alias	发送者别名
GetChatInfoUrl	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
MsgType	消息类型，此时固定是attachment
Attachment	用户点击的attachment，目前只支持button
Attachment.CallbackId	attachment中设置的回调id
Attachment.Actions	用户点击的action信息
Attachment.Actions.Name	用户点击按钮的名字
Attachment.Actions.Value	用户点击按钮的值
Attachment.Actions.Type	用户点击按钮的类型，目前仅支持button类型
json协议格式如下：

{
    "webhook_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK",
    "msgid":"0GLL5fDZQF-1ygUp_4ECfAAA",
    "chatid":"CHATID",
	"postid": "POSTID",
    "chattype":"group",
    "from":{
        "userid":"zhangsan",
        "name":"张三",
        "alias":"zhangsan"
    },
    "get_chat_info_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=8odlJWtPSIwhuB48MsSd0MH0exGVu2VJsB5dM1QII2g",
    "msgtype":"attachment",
    "attachment":{
        "callbackid":"btn_for_show_more",
        "actions":[
            {
                "name":"btn_more",
                "value":"btn_more",
                "type":"button"
            }
        ]
    }
}
json协议参数说明：

参数	说明
webhook_url	机器人主动推送消息的url
msgid	消息Id，可用于去重
chatid	会话id，可能是群聊，也可能是单聊，也可能是小黑板
postid	小黑板帖子id，当前消息为小黑板回帖消息时带上
chattype	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
from	该消息发送者的信息
from.userId	发送者的userid
from.name	发送者姓名
from.alias	发送者别名
get_chat_info_url	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
msgtype	消息类型，此时固定是attachment
attachment	用户点击的attachment，目前只支持button
attachment.callbackid	attachment中设置的回调id
attachment.actions	用户点击的action信息
attachment.actions.name	用户点击按钮的名字
attachment.actions.value	用户点击按钮的值
attachment.actions.type	用户点击按钮的类型，目前仅支持button类型
 

图文混排消息
xml协议格式如下：

<xml>
	<WebhookUrl><![CDATA[http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK]]></WebhookUrl>
	<MsgId><![CDATA[CAEQi5HR8wUY/NGagIOAgAMgXQ==]]></MsgId>
	<ChatId><![CDATA[CHATID]]></ChatId>
	<ChatType><![CDATA[group]]></ChatType>
	<From>
		<UserId><![CDATA[T434200000]]></UserId>
		<Name><![CDATA[张三]]></Name>
		<Alias><![CDATA[jackzhang]]></Alias>
	</From>
	<GetChatInfoUrl><![CDATA[https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE]]></GetChatInfoUrl>
	<MsgType><![CDATA[mixed]]></MsgType>
	<MixedMessage>
		<MsgItem>
			<MsgType><![CDATA[text]]></MsgType>
			<Text>
				<Content><![CDATA[@机器人 这是今日的测试情况]]></Content>
			</Text>
		</MsgItem>
		<MsgItem>
			<MsgType><![CDATA[image]]></MsgType>
			<Image>
				<ImageUrl><![CDATA[http://p.qpic.cn/pic_wework/2698515288/54528347764eac2d194c2ce90d83769c62e478f59e706815/0]]></ImageUrl>
			</Image>
		</MsgItem>
	</MixedMessage>
</xml>
xml协议参数说明：

参数	说明
WebhookUrl	机器人主动推送消息的url
MsgId	消息Id，可用于去重
ChatId	会话id，可能是群聊，也可能是单聊，也可能是小黑板
PostId	小黑板帖子id，当前消息为小黑板回帖消息时带上
ChatType	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
From	该消息发送者的信息
From.UserId	发送者的userid
From.Name	发送者姓名
From.Alias	发送者别名
GetChatInfoUrl	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
MsgType	消息类型，此时固定是mixed
MixedMessage	图文混排消息，可由多个MsgItem组成
MixedMessage.MsgItem	图文混排消息中的某一张图片或者一段文字消息
MixedMessage.MsgItem.MsgType	MixedMessage.MsgItem的消息类型，可以是text或者image类型
MixedMessage.MsgItem.Text	MixedMessage.MsgItem的消息类型为text时,文本消息的详细内容
MixedMessage.MsgItem.Text.Content	文本内容
MixedMessage.MsgItem.Image	MixedMessage.MsgItem的消息类型为image时,图片消息的详细内容
MixedMessage.MsgItem.Image.ImageUrl	图片的url，注意不可在网页引用该图片
 

json协议格式如下：

{
    "webhook_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/send?key=WEBHOOK",
    "msgid":"CAIQrcjMjQYY/NGagIOAgAMg6PDc/w0=",
    "chatid":"CHATID",
    "chattype":"single",
    "from":{
        "userid":"T434200000",
        "name":"张三",
        "alias":"zhangsan"
    },
    "get_chat_info_url":"http://in.qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=CODE",
    "msgtype":"mixed",
    "mixed_message":{
        "msg_item":[
            {
                "msg_type":"text",
                "text":{
                    "content":"@机器人 这是今日的测试情况"
                }
            },
            {
                "msg_type":"image",
                "image":{
                    "image_url":"http://p.qpic.cn/pic_wework/2698515288/54528347764eac2d194c2ce90d83769c62e478f59e706815/0"
                }
            }
        ]
    }
}
json协议参数说明：

参数	说明
webhook_url	机器人主动推送消息的url
msgid	消息Id，可用于去重
chatid	会话id，可能是群聊，也可能是单聊，也可能是小黑板
postid	小黑板帖子id，当前消息为小黑板回帖消息时带上
chattype	会话类型，single，group，blackboard和blackboard_reply，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复，目前仅单聊支持回调图片
from	该消息发送者的信息
from.userId	发送者的userid
from.name	发送者姓名
from.alias	发送者别名
get_chat_info_url	获取会话信息的URL，有效时间5分钟，且仅能调用一次。详情参考获取会话信息
msgtype	消息类型，此时固定是mixed
mixed_message	图文混排消息，可由多个msg_item组成
mixed_message.msg_item	图文混排消息中的某一张图片或者一段文字消息
mixed_message.msg_item.msg_type	mixed_message.msg_item的消息类型，可以是text或者image类型
mixed_message.msg_item.text	mixed_message.msg_item的消息类型为text时,文本消息的详细内容
mixed_message.msg_item.text.content	文本内容
mixed_message.msg_item.image	mixed_message.msg_item的消息类型为image时,图片消息的详细内容
mixed_message.msg_item.image.image_url	图片的url，注意不可在网页引用该图片
 

加密与回复
开发者解密数据得到用户消息内容后，可以选择直接回复空包，后续再通过webhook地址主动发送消息到群里，也可以在响应本次请求的时候直接回复消息。回复的消息需要先按明文协议和机器人回调协议(xml或json)构造数据包，然后对明文消息数据包进行加密，之后再回复最终的密文数据包。

当机器人回调协议为xml时，构造的xml数据包，并使用xml的加密库加密后得到密文数据包
当机器人回调协议为json时，构造的json数据包，并使用json的加密库加密后得到密文数据包
回复的明文消息结构体
被动回复的明文消息支持文本与markdown两种类型，其中文本消息支持@某位成员。

回复文本消息
xml明文协议示例

<xml>
	<MsgType>text</MsgType>
	<VisibleToUser>zhangsan|lisi</VisibleToUser>
	<Text>
		<Content><![CDATA[hello\nI'm RobotA\n]]></Content>
		<MentionedList>
			<Item><![CDATA[zhangsan]]></Item>
			<Item><![CDATA[@all]]></Item>
		</MentionedList>
		<MentionedMobileList>
			<Item><![CDATA[@all]]></Item>
			<Item><![CDATA[1380000000]]></Item>
		</MentionedMobileList>
	</Text>
</xml>
xml明文协议参数说明：

参数	说明
MsgType	此时固定为text
VisibleToUser	选填，有该参数时，该消息只有指定的群成员可见，其他成员不可见，多个userid用‘|’分隔
Text	文本消息的详细内容
Text.Content	文本内容
Text.MentionedList.Item	userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人
Text.MentionedMobileList.Item	手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
json明文协议示例

{
    "visible_to_user": "zhangsan|lisi",
    "msgtype": "text",
    "text": {
        "content": "hello\nI'm RobotA\n",
        "mentioned_list":["zhangsan","@all"],
        "mentioned_mobile_list":["@all","13800001111"]
    }
}
json明文协议参数说明：

参数	说明
msgtype	此时固定为text
visible_to_user	选填，有该参数时，该消息只有指定的群成员可见，其他成员不可见，多个userid用‘|’分隔
text	文本消息的详细内容
text.content	文本内容
text.mentioned_list	userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人
text.mentioned_mobile_list	手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
 

回复markdown消息
xml明文协议示例

<xml>
	<MsgType>markdown</MsgType>
	<VisibleToUser>zhangsan</VisibleToUser>
	<Markdown>
		<Content><![CDATA[实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n>类型:<font color=\"comment\">用户反馈</font> \n>普通用户反馈:<font color=\"comment\">117例</font> \n >VIP用户反馈:<font color=\"comment\">15例</font>]]></Content>
		<Attachment>
			<CallbackId><![CDATA[btn_for_show_more]]></CallbackId>
			<Actions>
				<Name><![CDATA[btn_more]]></Name>
				<Value><![CDATA[btn_more]]></Value>
				<Text><![CDATA[查看更多]]></Text>
				<Type>button</Type>
				<BorderColor>2EAB49</BorderColor>
				<TextColor>2EAB49</TextColor>
				<ReplaceText><![CDATA[select the button_more.]]></ReplaceText>
			</Actions>
		</Attachment>
	</Markdown>
</xml>
xml明文协议参数说明：

参数	说明
MsgType	此时固定为markdown
Markdown	消息详情
VisibleToUser	选填，有该参数时，该消息只有指定的群成员可见，其他成员不可见，多个userid用‘|’分隔
Content	markdown内容,支持的markdown语法与api一致
Attachment	选填，attachment内容，目前仅支持button类型
Attachment的参数说明：

参数	说明
CallbackId	Attachment对应的回调id，企业微信在回调时会透传该值
Actions	Attachment动作， 可支持多个
Name	Actions名字，企业微信回调时会透传该值， 最长不超过64字节
Value	Actions的值，企业微信回调时会透传该值，最长不超过128字节
Text	需要展示的文本，最长不超过128字节
Type	Actions类型，目前仅支持按钮
BorderColor	选填，按钮边框颜色
TextColor	选填，按钮文字颜色
ReplaceText	选填，点击按钮后替换的文本，不填则点击后不替换，最长不超过128字节
json明文协议示例

{
    "msgtype":"markdown",
    "markdown":{
        "content":"实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n>类型:<font color=\"comment\">用户反馈</font> \n>普通用户反馈:<font color=\"comment\">117例</font> \n >VIP用户反馈:<font color=\"comment\">15例</font>",
        "attachments":[
            {
				"callback_id":"btn_for_show_more",
                "actions":[
                    {
                        "border_color":"2EAB49",
                        "name":"btn_more",
                        "replace_text":"select the button_more.",
                        "text":"查看更多",
                        "text_color":"2EAB49",
                        "type":"button",
                        "value":"btn_more"
                    }
                ]
            }
        ]
    }
}
json明文协议参数说明：

参数	说明
msgtype	此时固定为markdown
visible_to_user	选填，有该参数时，该消息只有指定的群成员可见，其他成员不可见，多个userid用‘|’分隔
markdown	消息详情
markdown.content	markdown内容,支持的markdown语法与api一致
attachments	选填，attachment内容，目前仅支持button类型
attachments的参数说明：

参数	说明
callback_id	attachment对应的回调id，企业微信在回调时会透传该值
actions	attachment动作， 可支持多个
actions.name	actions名字，企业微信回调时会透传该值， 最长不超过64字节
actions.value	actions的值，企业微信回调时会透传该值，最长不超过128字节
actions.text	需要展示的文本，最长不超过128字节
actions.type	actions类型，目前仅支持按钮
actions.border_color	选填，按钮边框颜色
actions.text_color	选填，按钮文字颜色
actions.replace_text	选填，点击按钮后替换的文本，不填则点击后不替换，最长不超过128字节
 

加密后的协议
构造完成上述中的明文消息结构体之后，需要对其进行加密，然后填充到下述协议中的Encrypt字段中。加密过程参见“明文msg的加密过程”。

xml加密后的协议

<xml>
   <Encrypt><![CDATA[msg_encrypt]]></Encrypt>
   <MsgSignature><![CDATA[msg_signature]]></MsgSignature>
   <TimeStamp>timestamp</TimeStamp>
   <Nonce><![CDATA[nonce]]></Nonce>
</xml>
xml加密后的协议参数说明:

参数	是否必须	说明
Encrypt	是	加密后的消息内容
MsgSignature	是	消息签名
TimeStamp	是	秒级时间戳
Nonce	是	随机数，由开发者自行生成，必须保证两个小时内不重复
 

json加密后的协议

{
    "encrypt":"msg_encrypt",
    "msgsignature":"msg_signaturet",
    "timestamp": 111111111,
    "nonce":"nonce"
}
json加密后的协议参数说明:

参数	是否必须	说明
encrypt	是	加密后的消息内容
msgsignature	是	消息签名
timestamp	是	秒级时间戳
nonce	是	随机数，由开发者自行生成，必须保证两个小时内不重复
 

获取会话信息
在开启了回调的情况下，每次回调会带上一个临时有效的URL，可以使用http GET请求获取会话信息。
该URL有效期只有５分钟，且调用一次后失效

curl "https://qyapi.weixin.qq.com/cgi-bin/webhook/get_chat_info?code=irR1qrQ5B6V0Y-T4xwInFWtl73iMJOv7E-5QT5CQi54"
返回数据示例如下:

{
  "errcode": 0,
  "errmsg": "ok",
  "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
  "name": "吃货群",
  "chattype": "group",
  "members": [
    {
      "userid": "T23860001A",
      "alias": "zhangsan",
      "name": "张三"
    },
    {
      "userid": "T05720007A",
      "alias": "lisi",
      "name": "李四"
    },
    {
      "userid": "T30290007A",
      "alias": "wangwu",
      "name": "王五"
    }
  ]
}
参数	说明
chatid	会话ID，唯一标识一个会话
name	会话名, 会话类型为 group，blackboard和blackboard_reply时提供会话名
chattype	会话类型，目前有single，group，blackboard和blackboard_reply四种类型，分别表示：单聊，群聊，小黑板帖子和小黑板帖子回复
members	会话成员列表
member.userid	用户ID
member.alias	用户别名
member.name	用户姓名
通过code获取命令信息
在某些场景下，企业微信将直接通过webview打开用户配置的页面。访问页面的同时，会附带一个code在url参数上，用户可用此code获取命令信息。
获取此类code的场景包括：

机器人斜杠命令。命令配置为打开url型，当用户执行命令后；
需注意：

code 5分钟内有效
code只能使用一次
请求方式:GET(HTTPS)

请求地址:https://qyapi.weixin.qq.com/cgi-bin/webhook/get_command_info?code=xxxxxx

参数说明:

参数	必须	说明
code	是	临时凭证，打开web页面回调时，附带在url参数上。
权限说明: (无特殊权限)

返回结果:

{
    "from": {
        "userid": "zhangsan",
        "name": "张三",
        "alias": "zs"
    },
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
    "response_url": "https://qyapi.weixin.qq.com/xxxxxxx",
    "slash_command": {
        "name": "/todo",
        "param": "今天晚上取快递"
    },
    "errcode": 0,
    "errmsg": "ok"
}
参数说明:

参数	说明
from	触发命令的成员信息
from.userid	成员id
from.name	成员名字
from.alias	成员别名
chatid	群ID，唯一标识一个群
response_url	一个临时性的webhook地址，开发者可以用该地址回复消息以便响应该事件
需注意：24小时内有效且只能使用一次
slash_command	斜杠命令详情(斜杠命令打开URL时返回)
slash_command.name	斜杠命令名称
slash_command.param	斜杠命令参数
机器人接受消息协议设置
机器人接受消息协议支持xml和json格式，默认为xml格式。其中xml协议字段命名风格为驼峰样式，json协议字段命名风格为下划线+小写，开发者可以根据自身业务灵活选择。

开发者可以通过机器人接受消息url后面添加参数robot_callback_format=json/xml来设置回调方式，
举个例子：
假设机器人接受消息url为https://test.woa.com/bot_callback，
设置接受消息url地址为https://test.woa.com/bot_callback?robot_callback_format=json，则机器人收到的回调包为json格式
设置接受消息url地址为https://test.woa.com/bot_callbackbot?robot_callback_format=xml，机器人收到的回调包为xml格式

特殊的，sections消息和模块化消息，模版卡片消息的回调事件中默认情况下xml回调协议字段命名和json一样为小写加下划线，可以通过在回调协议后面设置robot_callback_format=xml设置，则xml协议的字段名为驼峰样式
上一篇
群机器人接口说明（内测）
下一篇
机器人发消息接口
关于腾讯
用户协议
帮助中心
© 1998 - 2025 Tencent Inc. All Rights Reserved
本节内容
概述
回调加密方案
设置接收消息的参数
验证URL有效性
接收与解密
接收消息的说明
接收密文协议
解密后的消息结构体
文本消息
图片消息
事件消息
attachment事件消息
图文混排消息
加密与回复
回复的明文消息结构体
回复文本消息
回复markdown消息
加密后的协议
获取会话信息
通过code获取命令信息
机器人接受消息协议设置


复制到剪贴板 反馈纠错
企业内部开发
快速入门
服务端API
客户端API
工具与资源
附录
更新日志
联系我们

基础

连接微信

办公
企业内部开发
服务端API
消息推送
群机器人
群机器人接口说明（内测）
群机器人接口说明（内测）
最后更新：2025/06/04
更新日志
支持文件类型的消息，查看详情
支持用户向机器人发起单聊会话，此时向机器人回调enter_chat事件，查看详情
机器人收到回调事件或回调消息时，可取出chatid，并使用该chatid作为参数向指定会话发消息，查看详情
markdown支持attachment（带按钮的消息），查看详情
发往指定群里的消息，支持指定某个群成员可见（其他成员收不到该消息），查看详情
用户与机器人单聊时，支持回调图片消息，查看详情
用户可向机器人发送图文混排消息，并支持回调图文混排消息，查看详情
支持机器人在小黑板中发text，markdown和image类型消息的帖子和帖子回复，查看详情
新增企业微信机器人demo，使用腾讯云快速部署企业微信机器人，查看详情
新增机器人发送模版卡片类型消息，查看详情
新增机器人发送 markdown_v2 类型消息，查看详情
 

如何使用群机器人
在终端某个群组添加机器人之后，可以获取到webhook地址，然后开发者用户按以下说明构造post data向这个地址发起HTTP POST 请求，即可实现给该群组发送消息。下面举个简单的例子.
假设webhook是：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=633a31f6-xxxx-xxxx-xxxx-0ec1eefaaaa
特别特别要注意：一定要保护好机器人的webhook地址，避免泄漏！不要分享到github、博客等可被公开查阅的地方，否则坏人就可以用你的机器人来发垃圾消息了。
以下是用curl工具往群组推送文本消息的示例（注意要将url替换成你的机器人webhook地址，content必须是utf8编码）：

curl 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=633a31f6-xxxx-xxxx-xxxx-0ec1eefaaaaa' \
   -H 'Content-Type: application/json' \
   -d '
   {
    	"chatid": "wrkSFfCgAAtMxxx4xqDatM5C9IDHFaaa",
    	"msgtype": "text",
    	"text": {
        	"content": "hello world"
    	}
   }'
当前自定义机器人支持文本（text）、markdown（markdown、markdown_v2）、图片（image）、图文（news）、文件（file）、语音（voice）、模板卡片（template_card）八种消息类型。
机器人的text/markdown类型消息支持在content中使用<@userid>扩展语法来@群成员（markdown_v2类型消息不支持该扩展语法）
消息类型及数据格式
文本类型
{
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw|zhangsan",
	"post_id" : "bpkSFfCgAAWeiHNo2p6lJbG3_F2xxxxx",
	"visible_to_user": "zhangsan|lisi",
    "msgtype": "text",
    "text": {
        "content": "<@zhangsan>广州今日天气：29度，大部分多云，降雨概率：60%",
		"mentioned_list":["wangqing","@all"],
		"mentioned_mobile_list":["13800001111","@all"]
    }
}
参数	是否必填	说明
chatid	否	会话id，支持最多传100个，用‘|’分隔。可能是群聊会话，也可能是单聊会话或者小黑板会话，通过消息回调获得，也可以是userid。 特殊的，当chatid为“@all_group”时，表示对所有群和小黑板广播，为“@all”时，表示对所有群和所有小黑板广播。不填则默认为“@all_group”。
post_id	否	小黑板帖子id，有且只有chatid指定了一个小黑板的时候生效
msgtype	是	消息类型，此时固定为text
content	是	文本内容，最长不超过2048个字节，必须是utf8编码
mentioned_list	否	userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人，如果开发者获取不到userid，可以使用mentioned_mobile_list，目前 mentioned_list 暂不支持小黑板
mentioned_mobile_list	否	手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人，目前 mentioned_mobile_list 暂不支持小黑板
visible_to_user	否	该消息只有指定的群成员或小黑板成员可见（其他成员不可见），有且只有chatid指定了一个群或一个小黑板的时候生效，多个userid用‘|’分隔
 



 

markdown类型
{
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
	"post_id" : "bpkSFfCgAAWeiHNo2p6lJbG3_F2xxxxx",
	"msgtype": "markdown",
	"visible_to_user": "zhangsan",
	"markdown": {
		"content": "**2019公司文化衫尺码收集**\n\n主题：2019文化衫尺码收集\n范围：所有<font color=\"warning\">正式员工+实习生</font>\n服装：统一为蓝色logo+白色T\n\n请选择你需要的尺码\n<@zhangsan><@lisi>",
		"at_short_name" : true,
		"attachments": [{
			"callback_id": "button_two_row",
			"actions": [{
					"name": "button_1",
					"text": "S",
					"type": "button",
					"value": "S",
					"replace_text": "你已选择S",
					"border_color": "#2EAB49",
					"text_color": "#2EAB49"
				},
				{
					"name": "button_2",
					"text": "M",
					"type": "button",
					"value": "M",
					"replace_text": "你已选择M",
					"border_color": "#2EAB49",
					"text_color": "#2EAB49"
				},
				{
					"name": "button_3",
					"text": "L",
					"type": "button",
					"value": "L",
					"replace_text": "你已选择L",
					"border_color": "#2EAB49",
					"text_color": "#2EAB49"
				},
				{
					"name": "button_4",
					"text": "不确定",
					"type": "button",
					"value": "不确定",
					"replace_text": "你已选择不确定",
					"border_color": "#2EAB49",
					"text_color": "#2EAB49"
				},
				{
					"name": "button_5",
					"text": "不参加",
					"type": "button",
					"value": "不参加",
					"replace_text": "你已选择不参加",
					"border_color": "#2EAB49",
					"text_color": "#2EAB49"
				}
			]
		}
		]
	}
}
参数	是否必填	说明
chatid	否	会话id，支持最多传100个，用‘|’分隔。可能是群聊会话，也可能是单聊会话或者小黑板会话，通过消息回调获得，也可以是userid。 特殊的，当chatid为“@all_group”时，表示对所有群广播，为“@all_blackboard”时，表示对所有小黑板广播，为“@all”时，表示对所有群和所有小黑板广播。不填则默认为“@all_group”。
post_id	否	小黑板帖子id，有且只有chatid指定了一个小黑板的时候生效
msgtype	是	消息类型，此时固定为markdown
content	是	markdown内容，最长不超过4096个字节，必须是utf8编码
at_short_name	否	markdown内容中@人指定为的短名字的方式，类型为bool值，设置为true则markdown中@xxx的表现为短名
attachments	否	attachments内容，目前仅支持button类型
visible_to_user	否	该消息只有指定的群成员或小黑板成员可见（其他成员不可见），有且只有chatid指定了一个群或一个小黑板的时候生效，多个userid用‘|’分隔
attachments的参数说明：

参数	是否必填	说明
callback_id	是	attachments对应的回调id，企业微信在回调时会透传该值
actions	是	attachments动作， 一个attachment中最多支持20个action
type	是	action类型，目前仅支持按钮
name	是	action名字，企业微信回调时会透传该值， 最长不超过64字节。为了区分不同的按钮，建议开发者自行保证name的唯一性
text	是	需要展示的文本，最长不超过128字节
border_color	否	按钮边框颜色
text_color	否	按钮文字颜色
value	是	action的值，企业微信回调时会透传该值，最长不超过128字节
replace_text	是	点击按钮后替换的文本，最长不超过128字节


目前支持的markdown语法是如下的子集：

标题 （支持1至6级标题，注意#与文字中间要有空格）
# 标题一
## 标题二
### 标题三
#### 标题四
##### 标题五
###### 标题六
加粗
**bold**
链接
[这是一个链接](https://work.weixin.qq.com/api/doc)
行内代码段（暂不支持跨行）
`code`
引用
> 引用文字
字体颜色(只支持3种内置颜色)
<font color="info">绿色</font>
<font color="comment">灰色</font>
<font color="warning">橙红色</font>
markdown_v2类型
{
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
	"msgtype": "markdown_v2",
	"visible_to_user": "zhangsan",
	"markdown_v2": {
         "content": "# 一、标题\n## 二级标题\n### 三级标题\n# 二、字体\n*斜体*\n\n**加粗**\n# 三、列表 \n- 无序列表 1 \n- 无序列表 2\n  - 无序列表 2.1\n  - 无序列表 2.2\n1. 有序列表 1\n2. 有序列表 2\n# 四、引用\n> 一级引用\n>>二级引用\n>>>三级引用\n# 五、链接\n[这是一个链接](https:work.weixin.qq.com\/api\/doc)\n![](https://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png)\n# 六、分割线\n\n---\n# 七、代码\n`这是行内代码`\n```\n这是独立代码块\n```\n\n# 八、表格\n| 姓名 | 文化衫尺寸 | 收货地址 |\n| :----- | :----: | -------: |\n| 张三 | S | 广州 |\n| 李四 | L | 深圳 |\n"
	   }
}
参数	是否必填	说明
chatid	否	会话id，支持最多传100个，用‘|’分隔。可能是群聊会话，也可能是单聊会话，通过消息回调获得，也可以是userid。 特殊的，当chatid为“@all_group” 和 “@all”时，表示对所有群广播。不填则默认为“@all_group”。
msgtype	是	消息类型，此时固定为markdown_v2。
该消息类型不支持发送到小黑板中
content	是	markdown_v2内容，最长不超过4096个字节，必须是utf8编码。
特殊的，
1. markdown_v2不支持字体颜色、@群成员的语法， 具体支持的语法可参考下面说明
2. 消息内容在客户端 4.1.36 版本以下(安卓端为4.1.38以下) 消息表现为纯文本，建议使用最新客户端版本体验
visible_to_user	否	该消息只有指定的群成员，有且只有chatid指定了一个群时候生效，多个userid用‘|’分隔




目前支持的markdown_v2语法是如下的子集：

标题 （支持1至6级标题，注意#与文字中间要有空格）
# 标题一
## 标题二
### 标题三
#### 标题四
##### 标题五
###### 标题六
字体
*斜体*
**加粗**
列表
- 无序列表 1
- 无序列表 2
 - 无序列表 2.1
 - 无序列表 2.2
1. 有序列表 1
2. 有序列表 2
引用
>一级引用
>>二级引用
>>>三级引用
链接
[这是一个链接](https://work.weixin.qq.com/api/doc)
![这是一个图片](https://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png)
分割线

---
代码
`这是行内代码`

```
这是独立代码块
```

表格
| 姓名 | 文化衫尺寸 | 收货地址 |
| :----- | :----: | -------: |
| 张三 | S | 广州 |
| 李四 | L | 深圳 |
图片类型
{
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
    "msgtype": "image",
	"visible_to_user": "zhangsan",
    "image": {
        "base64": "DATA",
		"md5": "MD5"
    }
}
参数	是否必填	说明
chatid	否	会话id，支持最多传100个，用‘|’分隔。可能是群聊会话，可能是单聊会话，也可能是小黑板会话，通过消息回调获得，也可以是userid。 特殊的，当chatid为"@all_group"时，表示对所有群广播，为"@all"时，表示对所有群广播。不填则默认为"@all_group"。
msgtype	是	消息类型，此时固定为image
base64	是	图片内容的base64编码
md5	是	图片内容（base64编码前）的md5值
visible_to_user	否	该消息只有指定的群成员可见（其他成员不可见），有且只有chatid指定了一个群的时候生效，多个userid用‘|’分隔
注：图片（base64编码前）最大不能超过2M，支持JPG,PNG格式


图文类型
{
    "chatid": "wrkSFfCgAAtMQKg4xqDatM5C9IDHFpTw",
    "msgtype": "news",
	"visible_to_user": "zhangsan",
    "news": {
       "articles" : [
           {
               "title" : "中秋节礼品领取",
               "description" : "今年中秋节公司有豪礼相送",
               "url" : "URL",
               "picurl" : "https://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png"
           }
        ]
    }
}
参数	是否必填	说明
chatid	否	会话id，支持最多传100个，用‘|’分隔。可能是群聊会话，也可能是单聊会话，通过消息回调获得，也可以是userid。 特殊的，当chatid为“@all_group”时，表示对所有群广播，为“@all”时，表示对所有群广播。不填则默认为“@all_group”。
msgtype	是	消息类型，此时固定为news
articles	是	图文消息，一个图文消息支持1到8条图文
title	是	标题，不超过128个字节，超过会自动截断
description	否	描述，不超过512个字节，超过会自动截断
url	是	点击后跳转的链接。
picurl	否	图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。
visible_to_user	否	该消息只有指定的群成员可见（其他成员不可见），有且只有chatid指定了一个群的时候生效，多个userid用‘|’分隔


小程序类型
{
    "msgtype": "miniprogram",
    "miniprogram": {
 		"title": "小程序测试消息",
 		"pic_media_id": "MEDIA_ID",
		"appid": "wx8bd80126147dfAAA",
		"page": "/path/index.html"
    }
}
参数	是否必填	说明
msgtype	是	消息类型，此时固定为miniprogram
miniprogram.title	是	小程序消息标题，最长为64字节
miniprogram.pic_media_id	是	小程序消息封面的media_id，封面图建议尺寸为520*416 。其中media_id可以通过机器人文件上传接口上传图片类型文件获得
miniprogram.appid	是	小程序appid，必须是关联到企业的小程序应用
miniprogram.page	是	小程序page路径


文件类型
{
    "msgtype": "file",
    "file": {
 		"media_id": "3a8asd892asd8asd"
    }
}
参数	是否必填	说明
msgtype	是	消息类型，此时固定为file
media_id	是	文件id，通过下文的文件上传接口获取


模版卡片类型
点击前往查看模版卡片类型

 

文件上传接口
素材上传得到media_id，该media_id仅三天内有效
media_id只能是对应上传文件的机器人可以使用
请求方式：POST（HTTPS）
请求地址：https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=KEY&type=TYPE

使用multipart/form-data POST上传文件， 文件标识名为"media"
参数说明：

参数	必须	说明
key	是	调用接口凭证, 机器人webhookurl中的key参数
type	是	固定传file
POST的请求包中，form-data中媒体文件标识，应包含有 filename、filelength、content-type等信息

filename标识文件展示的名称。比如，使用该media_id发消息时，展示的文件名由该字段控制
请求示例：

POST https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=693a91f6-7xxx-4bc4-97a0-0ec2sifa5aaa&type=file HTTP/1.1
Content-Type: multipart/form-data; boundary=-------------------------acebdf13572468
Content-Length: 220

---------------------------acebdf13572468
Content-Disposition: form-data; name="media";filename="wework.txt"; filelength=6
Content-Type: application/octet-stream

mytext
---------------------------acebdf13572468--
返回数据：

{
   "errcode": 0,
   "errmsg": "ok",
   "type": "file",
   "media_id": "1G6nrLmr5EC3MMb_-zK1dDdzmd0p7cNliYu9V5w7o8K0",
   "created_at": "1380000000"
}
参数说明：

参数	说明
type	媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件(file)
media_id	媒体文件上传后获取的唯一标识，3天内有效
created_at	媒体文件上传时间戳
上传的文件限制：
所有文件size必须大于5个字节

图片（image）：10MB，支持JPG,PNG格式
语音（voice） ：2MB，播放长度不超过60s，仅支持AMR格式
视频（video） ：10MB，支持MP4格式
普通文件（file）：20MB
 

消息发送频率限制
每个机器人向每个特定的群聊或小黑板发送的消息不能超过100条/分钟。
每个机器人广播发送的消息不能超过100条/分钟。
机器人不能主动给用户发单聊消息，但用户在单聊会话中触发机器人回调的时候，机器人可以主动向用户发三条单聊消息。
机器人申请了订阅范围，可以主动订阅范围下的用户发送单聊消息。每个机器人给每个特定用户发送单聊消息不能超过100条/分钟。
每个机器人每分钟调用接口发消息不能超过10000条/分钟。
同一个机器人相同的请求body，限制不能有2个及以上的并发请求。
机器人订阅范围
可以向系统管理员申请为机器人配置订阅范围，配置之后，机器人可直接给订阅范围之内的成员推送单聊的消息。腾讯同事请在公司内网按机器人主动推送消息权限申请说明进行申请。

腾讯下的机器人给用户推送单聊消息，发消息的chatid可以为用户的rtx(英文名)
附录
机器人发消息常见错误码
此处仅列出机器人发消息接口灰度能力返回的错误码，更多的错误码可以参考全局错误码
错误码	说明
93005	不允许机器人向用户发送单聊消息。
可能原因：
1. 用户不在机器人订阅范围
2. 机器人给用户发送单聊消息超过频率限制
3. 用户设置不再接收机器人单聊消息
上一篇
群机器人配置说明
下一篇
群机器人回调说明（内测）
关于腾讯
用户协议
帮助中心
© 1998 - 2025 Tencent Inc. All Rights Reserved
本节内容
更新日志
如何使用群机器人
消息类型及数据格式
文本类型
markdown类型
markdown_v2类型
图片类型
图文类型
小程序类型
文件类型
模版卡片类型
文件上传接口
消息发送频率限制
机器人订阅范围
附录
机器人发消息常见错误码
