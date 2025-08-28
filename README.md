## 简单的CosyVoice 2 API调用

1. 按照`README_CosyVoice.md`配置环境，下载CosyVoice 2模型

2. 把你需要的说话人语音wav文件放到asset文件夹下，并在`cosy2.py`中添加相应的SPEAKER条目

3. 使用下列命令启动api.

   ```cmd
   python cosy2.py
   ```

4. api列表：

   ```shell
   localhost:8000/speakers # 返回可用的说话人列表
   localhost:8000/tts # 文字转语音，以文字和说话人为参数，返回格式为json，包括说话人、输入文本、生成的语音文件地址和时长
   localhost:8000/download # 下载生成的语音文件
   ```

   

