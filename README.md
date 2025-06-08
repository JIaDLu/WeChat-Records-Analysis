## 【Mac M2】获取WeChat聊天记录并用photon分析

#### 1，定位WeChat聊天记录位置

:gear:mac上微信的聊天记录都以数据库的形式保存在下面目录：

```
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application\ Support/com.tencent.xinWeChat/xxx/yyy/Message/*.db
```

![image-20231104210524431](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081605803.png)



![image-20231104210649369](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081606955.png)

这里需要注意的是，如果电脑登录过多个微信账号，在`2.0b4.0.9`文件夹下，可能存在多个文件夹，需要逐个查看哪个是你要导出聊天记录的账号。可以根据修改日期进行排序，一般就是那个最近修改过的文件夹。也可以根据文件大小进行判断，**一般占用内存大的文件夹就是我们要找的文件**。

###### 所有的微信聊天记录就保存在这个`Message` 目录下的db数据库文件，我们只需要拿到这个目录下的所有形如`msg_0.db`的数据库文件即可

:frowning:**这些数据库文件都是加密的**。不过微信存数据使用的是开源的 sqlcipher, 所以还是有办法导出微信在 Mac 本机的数据库的

#### 2，获取数据库的密钥

> 网上有很多方法【几乎对于mac都是这套方法】都是利用lldb对进程设断点跟踪信息，从而获取密钥。我的方法也是跟在许多博主那样做，但还是遇到一些bug。

:arrow_up_down:以下是按其他博主的方法 + 我遇到的bug的处理方法

1. 打开mac上的微信，但是不要登录！

   ![image-20231104211735092](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081606021.png)

2. 打开终端，输入

   ```bash
   sudo lldb -p $(pgrep WeChat)
   ```

   报错：

   ```bash
   error: attach failed: cannot attach to process
   ```

   解决方案：

   - mac电脑关机

   - 按住电源键10s【M系列】直到出现恢复模式界面

   - 点击顶部菜单【ul～】，然后打开终端

   - 在终端中输入`csrutil disable`，以关闭系统完整性保护（SIP）

     ![image-20231104212231940](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081615289.png)

   - 在终端中输入`reboot`，然后等待重启

   - 电脑重启后，重新在终端中执行`sudo lldb -p $(pgrep WeChat)`命令即可。（此时还是保持WeChat是打开的）

     【正常】

     ![image-20231104212608733](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081606814.png)

3. 进入lldb的子shell后，输入以下命令并回车

   ```bash
   br set -n sqlite3_key
   ```

4. 继续在终端中输入`c`，并回车

5. 这时候会弹出微信登录界面，登录即可（需要注意的是，这时候手机会提示微信已经在Mac中登录，但Mac上的微信可能会卡住，进不去微信，这里不用不用理会，继续下面的操作）

6. 继续在lldb的子shell中输入以下命令：

   ```bash
   memory read --size 1 --format x --count 32 $rsi
   ```

   报错： error: invalid start address expression. 		error: address expression "$rsi" evaluation failed

   ![image-20231104212757685](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081606314.png)

   解决：根据输出的内容，重新定义寄存器的位置。

   ![image-20231104213047478](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081607125.png)

7. 重新在lldb的子shell中输入以下命令：

   ```bash
   memory read --size 1 --format x --count 32 $x1
   ```

   ![image-20231104213429562](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081607936.png)

8. 接着用python脚本来处理这串编码，将上面的输出信息复制到脚本中的`source`变量中	

   ```python
   source = """
   0x600000d7f440: 0x1b 0x53 0xa8 0x35 0x2c 0xc5 0x4f 0x68
   0x600000d7f448: 0x8d 0x38 0xdd 0x99 0x15 0xcf 0xed 0x86
   0x600000d7f450: 0xf2 0xc5 0x7e 0xae 0xd7 0x99 0x48 0xab
   0x600000d7f458: 0x93 0xf1 0x6f 0x9a 0x40 0x50 0x2a 0xd6
   """
   key = '0x' + ''.join(i.partition(':')[2].replace('0x', '').replace(' ', '') for i in source.split('\n')[1:5])
   print(key)
   
   ```

   ![image-20231104213901629](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081608530.png)

#### 3，使用sqlitebrowser打开【能连database就可以】

下载地址如下：https://sqlitebrowser.org/dl/

汇总聊天记录的数据库：

![image-20231104214329440](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081608012.png)

安装并打开软件 → 打开数据库 → 选择前面提到的形如`msg_0.db`的数据库文件 → 这时候会弹出输入密码的窗口，选择`raw key`和`SQLCipher 3 defaults` 选项 → 输入获取到的数据库密码 → 这时候可以看到db文件被正常打开了

![image-20231104214523766](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081608982.png)

:+1:connected successfully

![image-20231104214618960](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609579.png)

打开数据库后，可以看到这个`msg_0.db`数据库有28张表格，每张表格就是和一个人的单聊记录或者一个群组的聊天记录。可以在软件中选择文件菜单栏 → 选择导出 → 选择表到json → 这样就可以将这个数据库的所有的聊天记录导出为json文件了

#### 4，数据清洗和数据分析【python】

字段信息：

```python
"CompressContent": null, # 转账金额信息，有+与-表示：收到与转出，默认为空
"ConBlob": "chN3eGlkX2dnNWpibzcyZGkyaTEyehN3eGlkX3BlMXMzenh6OThsajIykgF05paw5qKF5Zut57Sg6aOffumhv+m4vyA6IOaLm+eUn+S/oeaBrwrmrKLov47ovazlj5HvvIzlip/lvrfml6Dph4/vvIEK5pS26I635Y6o6Im677yM5pm65oWn5Lq655Sf77yBCiAg44CK5rOo5oSPIDouLi6AAQCYAQCgAQC4AQDIAQDQAQDwAQD4AQA=", #
"IntRes1": 0,
"IntRes2": 0,
"StrRes1": null,
"StrRes2": null,
"mesDes": 1, # 是否为自己发送的消息
"mesLocalID": 2, 
"mesSvrID": 1920754171758050414, # 服务端的消息ID 
"messageType": 1, # 消息类型，1为文本，3为图片，34为语音，47为表情包，43为视频，48为位置，49为文件信息，10000为系统消息
"msgContent": "你好！", # 消息内容
"msgCreateTime": 1626161450, # 创建时间（Unix时间戳）
"msgImgStatus": 1, # 图片的状态
"msgSeq": 711260330,
"msgSource": "",
"msgStatus": 4, # 消息状态，比如发送失败，成功，正在发送
"msgVoiceText": null
```

工作目录

```
- experiment
	- data										
		XXX.json    							 #将要分析的某个数据库的json文件放在experiment/data/下
	- picture   						     #此文件夹用于存放生成的分析图
	main.py 						         #main_coding
	cv_demo.py 							     #用于调试得到合适的masked图片
	raw.png       							 #用于制作含mask的云图的原图
	suitable_masked.png					 #raw.png在cv_demo.py中调试出来的合适的mask图
	fangsong.ttf 								 #制作云图用到的中文字体（仿宋）
	transport_code.py 					 # 转码，获取数据库的密钥
	
```

#### 5, 结果分析

可以参考main.py中的代码进行聊天记录的分析，本人所采用的分析结果展示如下：（此分析作为参考，可根据个人需求进行其他结果的分析）

##### 1, 计算一天中不同聊天时段记录数量的分布   wc.calculate_24hours_records()

![category](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609133.png)

##### 2，分析和对方的聊天记录总数  wc.calculate_records_count() 

![count](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609712.png)

##### 3，统计聊天记录中不同类型的数量 wc.statistics_records_catalogies()

![111](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609347.png)

##### 4，统计不同月份的聊天记录数 wc.analyze_monthly_records()

![WechatIMG210844](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609756.png)

##### 5，含masked的云图  wc.masked_divide_words(firname)

![image-20240126171724683](https://cdn.jsdelivr.net/gh/JIaDLu/BlogImg/img/202506081609772.png)

#### 6, If you have any questiones, please contact me.

mail: lujiadong0243@gmail.com

