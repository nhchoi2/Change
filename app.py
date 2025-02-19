import os
import io
import re
import mimetypes
import streamlit as st
from pydub import AudioSegment

#######################################
# 1. FFmpeg 및 ffprobe 경로 설정
#######################################
# 배포 환경(예: Streamlit Sharing)에서는 시스템 PATH에 설치된 ffmpeg/ffprobe 사용
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

# 로컬 Windows 테스트 시 아래 주석을 해제하여 절대 경로를 사용할 수 있습니다.
# ffmpeg_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
# ffprobe_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffprobe.exe"
# os.environ["FFMPEG_BINARY"] = ffmpeg_path
# os.environ["FFPROBE_BINARY"] = ffprobe_path
# AudioSegment.converter = ffmpeg_path
# AudioSegment.ffprobe = ffprobe_path

#######################################
# 2. 지원 포맷 및 기본 설정
#######################################
SUPPORTED_FORMATS = ["amr", "mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"]
DEFAULT_OUTPUT_FORMAT = "mp3"  # 안드로이드(갤럭시)에서 재생 가능한 MP3

#######################################
# 3. 시간 입력 검증 및 변환 함수
#######################################
def parse_time(time_str):
    """
    시간 문자열을 초 단위(float)로 변환합니다.
    - mm:ss 또는 hh:mm:ss 형식 또는 초 단위 숫자 문자열 지원.
    """
    try:
        time_str = time_str.strip()
        if ":" in time_str:
            parts = time_str.split(":")
            parts = [float(p) for p in parts]
            if len(parts) == 2:
                # mm:ss
                minutes, seconds = parts
                return minutes * 60 + seconds
            elif len(parts) == 3:
                # hh:mm:ss
                hours, minutes, seconds = parts
                return hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError
        else:
            return float(time_str)
    except Exception:
        raise ValueError("시간 형식이 올바르지 않습니다. 초 단위 숫자 또는 mm:ss (혹은 hh:mm:ss) 형식으로 입력하세요.")

#######################################
# 4. Streamlit UI 구성
#######################################
st.title("🎵 오디오 파일 변환 및 컷팅 앱")
st.write("다양한 오디오 파일을 업로드하여 MP3로 변환한 후, 원하는 구간을 컷팅(편집)하여 다운로드할 수 있습니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader("오디오 파일 업로드", type=SUPPORTED_FORMATS)

if uploaded_file is not None:
    # 파일 이름 및 확장자 추출
    file_name = uploaded_file.name
    file_extension = file_name.split(".")[-1].lower()
    
    # MIME 타입 감지 (경우에 따라 application/octet-stream으로 나올 수 있음)
    detected_type = mimetypes.guess_type(file_name)[0]
    st.write(f"업로드한 파일: `{file_name}`, 감지된 MIME: `{detected_type}`")
    
    # 파일 읽기 및 AudioSegment 로딩
    file_bytes = uploaded_file.read()
    try:
        original_audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=file_extension)
    except Exception as e:
        st.error(f"오디오 파일을 읽는 중 오류 발생:\n{e}")
        st.stop()
    
    #######################################
    # 5. 전체 MP3 파일 변환
    #######################################
    output_buffer = io.BytesIO()
    try:
        original_audio.export(output_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")
        output_buffer.seek(0)
    except Exception as e:
        st.error(f"MP3로 변환하는 중 오류 발생:\n{e}")
        st.stop()
    
    st.success("전체 파일 변환 성공!")
    st.download_button(
        label="🔽 전체 변환 MP3 다운로드",
        data=output_buffer,
        file_name=f"converted_{file_name.split('.')[0]}.{DEFAULT_OUTPUT_FORMAT}",
        mime="audio/mpeg"
    )
    
    #######################################
    # 6. 오디오 컷팅 (편집) 기능
    #######################################
    st.markdown("## 오디오 컷팅 (편집)")
    start_time_input = st.text_input("시작 시간 (초 또는 mm:ss 형식)", value="0")
    end_time_input = st.text_input("종료 시간 (초 또는 mm:ss 형식)", value="")
    
    if st.button("컷팅 실행"):
        try:
            start_sec = parse_time(start_time_input)
            if end_time_input.strip() == "":
                # 종료 시간이 비어 있으면 전체 길이를 사용
                end_sec = len(original_audio) / 1000.0
            else:
                end_sec = parse_time(end_time_input)
            
            # 시간 범위 검증
            total_sec = len(original_audio) / 1000.0
            if start_sec < 0 or end_sec <= start_sec or end_sec > total_sec:
                st.error("시간 범위가 올바르지 않습니다. 시작 시간은 0 이상, 종료 시간은 시작 시간보다 커야 하며 오디오 길이 이하여야 합니다.")
            else:
                # pydub은 밀리초 단위 사용
                start_ms = int(start_sec * 1000)
                end_ms = int(end_sec * 1000)
                cut_audio = original_audio[start_ms:end_ms]
                
                cut_buffer = io.BytesIO()
                cut_audio.export(cut_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")
                cut_buffer.seek(0)
                st.success("오디오 컷팅 성공!")
                st.download_button(
                    label="🔽 컷팅된 MP3 다운로드",
                    data=cut_buffer,
                    file_name=f"cut_{file_name.split('.')[0]}.{DEFAULT_OUTPUT_FORMAT}",
                    mime="audio/mpeg"
                )
        except Exception as e:
            st.error(f"오디오 컷팅 중 오류 발생:\n{e}")

st.write("⚙️ FFmpeg 및 ffprobe가 올바르게 설정되어야 변환 및 편집이 가능합니다.")
st.write("FFmpeg 다운로드: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)")
