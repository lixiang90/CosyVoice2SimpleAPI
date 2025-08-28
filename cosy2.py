from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import os

import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav
import torchaudio
import time
from pydub import AudioSegment

DEFAULT_SPEAKERS = {
    "default":(r"asset/zero_shot_prompt.wav","希望你以后能够做的比我还好呦。"),
    "xiaoxiao":(r"asset/xiaoxiao.wav","本文将借助三个环环相扣的宏观历史观，对古希腊罗马史的叙事形成过程进行辨伪分析，并以此为基础，回应“西方伪史论”争议，尝试提供一条超越简单“信”与“疑”的思考路径。"),
    "dingzhen":(r"asset/dingzhen.MP3","这何尝又不是我们的人生呢？我们努力学习就是为了寻找一个局部最优解。"),
    "xiaohaijie":(r"asset/xiaohaijie.WAV","我点的奶茶怎么还没到啊？烦死了，看一下！"),
    "shantianfang":(r"asset/shantianfang.WAV","从打今天开始，我给大家讲一部长篇历史故事————隋唐演义")
}

class CosyVoiceService:
    def __init__(self, speakers = DEFAULT_SPEAKERS):
        self.speakers = speakers
        self.cosyvoice = CosyVoice2(r'pretrained_models/CosyVoice2-0.5B', load_jit=False, load_trt=False, load_vllm=False, fp16=False)

    def get_audio(self, text: str, speaker: str = "default", language: str = "zh"):
        if speaker not in self.speakers.keys():
            raise ValueError(f"{speaker}: No such speaker.")
        prompt_speech_16k = load_wav(self.speakers[speaker][0], 16000)
        all_data = {"input_text":text,"speaker":speaker}
        wav_files = []
        duration = 0
        for i, j in enumerate(self.cosyvoice.inference_zero_shot(text, self.speakers[speaker][1], prompt_speech_16k, stream=False)):
            filename = f'generated/{speaker}_{time.time_ns()}.wav'
            torchaudio.save(filename, j['tts_speech'], self.cosyvoice.sample_rate)
            wav_files.append(filename)

        combined = AudioSegment.empty()
        for file in wav_files:
            audio = AudioSegment.from_file(file)
            duration += len(audio)
            combined += audio

        # 导出合并后的文件
        final_filename = f'generated/{speaker}_{time.time_ns()}.mp3'
        combined.export(final_filename, format="mp3")
        all_data["original_audio"] = final_filename
        all_data["duration"] = duration / 1000
        return all_data
    
# 创建 API 应用
app = FastAPI(title="CosyVoice API", version="1.0")
cosy_service = CosyVoiceService()

@app.get("/speakers")
def list_speakers():
    """返回可用的说话人列表"""
    return {"speakers": list(DEFAULT_SPEAKERS.keys())}

@app.post("/tts")
def tts(text: str = Query(..., description="要转换的文本"),
        speaker: str = Query("default", description="说话人名称")):
    """将文字转成语音，返回文件路径和可下载的链接"""
    try:
        result = cosy_service.get_audio(text=text, speaker=speaker)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/download")
def download(file: str):
    """下载生成的 wav 文件"""
    if not os.path.exists(file):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file, media_type="audio/wav", filename=os.path.basename(file))

if __name__ == "__main__":
    # 运行 API 服务
    uvicorn.run(app, host="0.0.0.0", port=8000)
        