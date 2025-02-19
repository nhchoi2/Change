import streamlit as st
import os
import io
from pydub import AudioSegment

# ✅ FFmpeg 실행 파일 경로 설정 (직접 다운로드한 경우)
FFMPEG_PATH = "ffmpeg.exe"  # Windows: 같은 폴더에 ffmpeg.exe 배치
# Linux/Mac의 경우: FFMPEG_PATH = "/usr/bin/ffmpeg" 또는 직접 다운로드한 경로 지정

# Pydub에 FFmpeg 경로 등록
AudioSegment.converter = FFMPEG_PATH

# ✅ Streamlit UI
st.title("🎵 음원 파일 변환기")
st.write("업로드한 오디오 파일을 원하는 형식으로 변환합니다.")

# ✅ 파일 업로드
uploaded_file = st.file_uploader("오디오 파일을 업로드하세요.", type=["mp3", "wav", "flac", "ogg", "m4a"])

# ✅ 변환 포맷 선택
output_format = st.selectbox("변환할 오디오 형식 선택", ["mp3", "wav", "flac", "ogg", "m4a"])

if uploaded_file is not None:
    # ✅ 파일 읽기
    st.audio(uploaded_file, format="audio/mp3")
    file_bytes = uploaded_file.read()

    # ✅ BytesIO를 이용한 변환
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=uploaded_file.type.split("/")[-1])
    output_buffer = io.BytesIO()
    audio.export(output_buffer, format=output_format)
    output_buffer.seek(0)

    # ✅ 변환된 파일 다운로드 버튼 제공
    st.download_button(
        label="🔽 변환된 파일 다운로드",
        data=output_buffer,
        file_name=f"converted.{output_format}",
        mime=f"audio/{output_format}"
    )

st.write("FFmpeg이 정상적으로 실행되는지 확인하려면 [FFmpeg 다운로드 가이드](https://www.gyan.dev/ffmpeg/builds/)를 참고하세요.")
