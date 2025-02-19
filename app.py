import os
import io
import mimetypes
import streamlit as st
from pydub import AudioSegment

#######################################
# 1. FFmpeg 및 ffprobe 절대 경로 설정
#######################################
# FFmpeg 및 ffprobe 실행 파일 경로 (절대 경로 사용)
ffmpeg_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffprobe.exe"

# 환경 변수에 등록
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path

# pydub에 경로 설정
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

#######################################
# 2. 지원 포맷 및 기본 설정
#######################################
SUPPORTED_FORMATS = ["amr", "mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"]
DEFAULT_OUTPUT_FORMAT = "mp3"  # 안드로이드(갤럭시)에서 재생 가능한 MP3

#######################################
# 3. Streamlit UI 구성
#######################################
st.title("🎵 다중 오디오 포맷 변환기")
st.write("여러 오디오 파일을 업로드하여 안드로이드(갤럭시)에서 재생 가능한 MP3로 변환합니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader("오디오 파일 업로드", type=SUPPORTED_FORMATS)

#######################################
# 4. 파일 처리 및 변환 로직
#######################################
if uploaded_file is not None:
    # 파일 이름 및 확장자 추출
    file_name = uploaded_file.name
    file_extension = file_name.split(".")[-1].lower()
    
    # MIME 타입 감지 (경우에 따라 application/octet-stream으로 나올 수 있음)
    detected_type = mimetypes.guess_type(file_name)[0]
    st.write(f"업로드한 파일: `{file_name}`, 감지된 MIME: `{detected_type}`")
    
    # 지원 포맷 체크
    if file_extension not in SUPPORTED_FORMATS:
        st.error(f"지원되지 않는 파일 형식입니다: {file_extension}")
    else:
        # 파일을 메모리로 읽어 AudioSegment 로드
        file_bytes = uploaded_file.read()
        try:
            audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=file_extension)
        except Exception as e:
            st.error(f"오디오 파일을 읽는 중 오류 발생:\n{e}")
            st.stop()
        
        # MP3로 변환하여 메모리 버퍼에 저장 (비트레이트 192kbps)
        output_buffer = io.BytesIO()
        try:
            audio.export(output_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")
            output_buffer.seek(0)
        except Exception as e:
            st.error(f"MP3로 변환 중 오류 발생:\n{e}")
            st.stop()
        
        # 변환된 파일 다운로드 버튼 제공
        st.download_button(
            label="🔽 변환된 MP3 다운로드",
            data=output_buffer,
            file_name=f"converted.{DEFAULT_OUTPUT_FORMAT}",
            mime="audio/mpeg"
        )

st.write("⚙️ FFmpeg 및 ffprobe가 올바르게 설정되어야 변환이 가능합니다.")
st.write("FFmpeg 다운로드: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)")
