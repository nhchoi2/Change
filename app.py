import os
import io
import mimetypes
import streamlit as st
from pydub import AudioSegment
import tempfile

#######################################
# 1. FFmpeg 및 ffprobe 절대 경로 설정
#######################################
# 배포 환경(예: Streamlit Sharing)에서는 시스템 PATH에 설치된 ffmpeg/ffprobe가 /usr/bin 에 있다고 가정합니다.
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"

#######################################
# 2. 지원 포맷 및 기본 설정 (AMR 만 지원)
#######################################
SUPPORTED_FORMATS = ["amr"]
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
                minutes, seconds = parts
                return minutes * 60 + seconds
            elif len(parts) == 3:
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
st.title("🎵 AMR 파일 변환 및 컷팅 앱")
st.write("AMR 파일을 업로드하여 MP3로 변환한 후, 원하는 구간을 컷팅(편집)하여 다운로드할 수 있습니다.")

# AMR 파일 업로드 (지원 포맷: AMR)
uploaded_file = st.file_uploader("AMR 파일 업로드", type=SUPPORTED_FORMATS)

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_extension = file_name.split(".")[-1].lower()
    detected_type = mimetypes.guess_type(file_name)[0]
    st.write(f"업로드한 파일: `{file_name}`, 감지된 MIME: `{detected_type}`")
    
    if file_extension not in SUPPORTED_FORMATS:
        st.error("지원되는 파일 형식은 AMR 뿐입니다.")
        st.stop()
    
    try:
        file_bytes = uploaded_file.read()
        # 임시 파일을 /tmp 디렉토리에 생성 (배포 환경에서 보통 /tmp는 쓰기가 허용됨)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".amr", dir="/tmp") as tmp_file:
            tmp_file.write(file_bytes)
            temp_file_path = tmp_file.name
        
        # 파일 권한을 모두 허용 (0o777)
        os.chmod(temp_file_path, 0o777)
        
        original_audio = AudioSegment.from_file(temp_file_path, format="amr")
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
                end_sec = len(original_audio) / 1000.0
            else:
                end_sec = parse_time(end_time_input)
            
            total_sec = len(original_audio) / 1000.0
            if start_sec < 0 or end_sec <= start_sec or end_sec > total_sec:
                st.error("시간 범위가 올바르지 않습니다. 시작 시간은 0 이상, 종료 시간은 시작 시간보다 커야 하며 오디오 길이 이하여야 합니다.")
            else:
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
