import streamlit as st
import io
from pydub import AudioSegment

# ✅ FFmpeg 경로 설정 (직접 다운로드한 경우)
AudioSegment.converter = "ffmpeg.exe"  # Windows의 경우. Linux/Mac은 /usr/bin/ffmpeg 경로 확인

# ✅ Streamlit UI
st.title("🎵 AMR 파일 변환기")
st.write("AMR 파일을 MP3 또는 WAV로 변환합니다.")

uploaded_file = st.file_uploader("AMR 파일을 업로드하세요.", type=["amr"])

if uploaded_file is not None:
    # ✅ AMR 파일을 MP3로 변환
    file_bytes = uploaded_file.read()
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="amr")

    output_format = "mp3"  # MP3로 변환
    output_buffer = io.BytesIO()
    audio.export(output_buffer, format=output_format)
    output_buffer.seek(0)

    # ✅ 변환된 파일 다운로드 버튼 제공
    st.download_button(
        label="🔽 변환된 MP3 파일 다운로드",
        data=output_buffer,
        file_name=f"converted.{output_format}",
        mime=f"audio/{output_format}"
    )

st.write("FFmpeg이 정상적으로 실행되는지 확인하려면 [FFmpeg 다운로드 가이드](https://www.gyan.dev/ffmpeg/builds/)를 참고하세요.")
