import streamlit as st
from pydub import AudioSegment
import io
import os
import requests
import zipfile

# FFmpeg 다운로드 및 설정 함수
def setup_ffmpeg():
    ffmpeg_path = "ffmpeg"
    if not os.path.exists(ffmpeg_path):
        st.info("FFmpeg을 다운로드하는 중입니다... (최초 실행 시 한 번만)")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        response = requests.get(ffmpeg_url)
        
        # FFmpeg 압축파일 저장
        with open("ffmpeg.zip", "wb") as file:
            file.write(response.content)

        # 압축 해제
        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            zip_ref.extractall("ffmpeg")

        os.remove("ffmpeg.zip")  # 압축 파일 삭제

        # FFmpeg 실행 파일 경로 설정
        extracted_folder = [f for f in os.listdir("ffmpeg") if "ffmpeg" in f][0]
        ffmpeg_bin = os.path.join("ffmpeg", extracted_folder, "bin", "ffmpeg.exe")
        AudioSegment.converter = ffmpeg_bin
    else:
        AudioSegment.converter = os.path.join("ffmpeg", "ffmpeg.exe")

# FFmpeg 초기 설정 실행
setup_ffmpeg()

# Streamlit UI
st.title("🎵 음원 변환기")

# 파일 업로드
uploaded_file = st.file_uploader("변환할 오디오 파일을 업로드하세요", type=["mp3", "wav", "flac", "ogg", "aac"])

# 변환할 포맷 선택
formats = {"MP3": "mp3", "WAV": "wav", "FLAC": "flac", "AAC": "aac", "OGG": "ogg"}
selected_format = st.selectbox("변환할 파일 형식을 선택하세요", list(formats.keys()))

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/*", start_time=0)

    # 변환 버튼
    if st.button("🎵 변환하기"):
        try:
            # 파일 불러오기
            audio = AudioSegment.from_file(uploaded_file)
            
            # 변환된 파일을 메모리에 저장
            output_format = formats[selected_format]
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=output_format)
            output_buffer.seek(0)

            # 변환된 파일 다운로드 버튼 제공
            st.success(f"변환 완료! 🎉 ({selected_format} 형식)")
            st.download_button(
                label=f"📥 {selected_format} 파일 다운로드",
                data=output_buffer,
                file_name=f"converted_audio.{output_format}",
                mime=f"audio/{output_format}"
            )
        except Exception as e:
            st.error(f"오류 발생: {e}")
