import os
import io
import mimetypes

import streamlit as st
from pydub import AudioSegment

#######################################
# 1) FFmpeg 절대 경로 설정
#######################################
# Windows 예시 (절대 경로):
ffmpeg_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"

# Linux/Mac (예: /usr/bin/ffmpeg) 사용자라면 위 경로를 바꿔주세요.

# 파이썬 환경 변수에 등록 + pydub에 경로 설정
os.environ["FFMPEG_BINARY"] = ffmpeg_path
AudioSegment.converter = ffmpeg_path

#######################################
# 2) 지원하는 오디오 포맷 & 출력 포맷 설정
#######################################
SUPPORTED_FORMATS = ["amr", "mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"]
DEFAULT_OUTPUT_FORMAT = "mp3"  # 갤럭시(안드로이드)에서 재생 잘 됨

#######################################
# 3) Streamlit UI 구성
#######################################
st.title("🎵 다중 오디오 포맷 변환기")
st.write("다양한 오디오 파일을 업로드하고, MP3로 변환하여 안드로이드(갤럭시)에서 재생 가능하도록 만듭니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader("오디오 파일 업로드", type=SUPPORTED_FORMATS)

#######################################
# 4) 업로드된 파일 처리 로직
#######################################
if uploaded_file is not None:
    # 파일 이름, 확장자
    file_name = uploaded_file.name
    file_extension = file_name.split(".")[-1].lower()
    
    # MIME 타입 확인 (종종 'application/octet-stream'으로 뜰 수 있음)
    detected_type = mimetypes.guess_type(file_name)[0]
    st.write(f"업로드한 파일: `{file_name}`, 감지된 MIME: `{detected_type}`")

    # 확장자 체크 (SUPPORTED_FORMATS 안에 있어야 함)
    if file_extension not in SUPPORTED_FORMATS:
        st.error(f"지원되지 않는 파일 형식입니다: {file_extension}")
    else:
        # 파일 읽기 (메모리)
        file_bytes = uploaded_file.read()

        # 1) pydub으로 AudioSegment 로딩
        #    - MIME이 application/octet-stream이라도 확장자로 처리
        #    - AMR, MP3, WAV 등
        try:
            audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=file_extension)
        except Exception as e:
            st.error(f"오디오 변환 중 오류가 발생했습니다.\n에러 메시지: {e}")
            st.stop()

        # 2) MP3로 변환
        output_buffer = io.BytesIO()
        try:
            audio.export(output_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")
            output_buffer.seek(0)
        except Exception as e:
            st.error(f"오디오 MP3 변환에 실패했습니다.\n에러 메시지: {e}")
            st.stop()

        # 3) 변환된 파일 다운로드 버튼
        st.download_button(
            label="🔽 변환된 MP3 다운로드",
            data=output_buffer,
            file_name=f"converted.{DEFAULT_OUTPUT_FORMAT}",
            mime="audio/mpeg"  # MP3 MIME
        )

st.write("⚙️ FFmpeg 최신 버전이 제대로 설정되어야 변환이 가능합니다.")
st.write("FFmpeg 다운로드 가이드: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)")
