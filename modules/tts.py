import edge_tts
import asyncio

async def _generate_audio(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

"""
Convert text to speech using Microsoft Edge TTS.
Some voice options:
English : en-US-AriaNeural, en-US-GuyNeural
French  : fr-FR-DeniseNeural
German  : de-DE-KatjaNeural
Chinese : zh-CN-XiaoxiaoNeural
Malay   : ms-MY-YasminNeural
"""
def text_to_speech(text, output_path="uploads/output_audio.mp3", voice="en-US-AriaNeural"):
    asyncio.run(_generate_audio(text, output_path, voice))
    return output_path