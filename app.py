import streamlit as st
import io
from pydub import AudioSegment

# ✅ 최신 FFmpeg 경로 설정 (수동 다운로드 후 프로젝트 폴더에 배치)
AudioSegment.converter = r"ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe" # Windows: 같은 폴더에 ffmpeg.exe 배치
# Linux/Mac은 "/usr/bin/ffmpeg"로 경로 설정 가능

# ✅ 지원하는 입력 포맷 (다양한 오디오 파일 변환 가능)
SUPPORTED_FORMATS = ["amr", "mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"]

# ✅ 안드로이드(갤럭시)에서 재생 가능한 최적 출력 포맷
DEFAULT_OUTPUT_FORMAT = "mp3"

# ✅ Streamlit UI
st.title("🎵 다중 오디오 포맷 변환기")
st.write("다양한 오디오 파일을 안드로이드(갤럭시)에서 재생 가능한 MP3로 변환합니다.")

# ✅ 파일 업로드
uploaded_file = st.file_uploader("오디오 파일을 업로드하세요.", type=SUPPORTED_FORMATS)

if uploaded_file is not None:
    # ✅ 원본 파일 확장자 확인
    original_format = uploaded_file.type.split("/")[-1]

    if original_format not in SUPPORTED_FORMATS:
        st.error(f"지원되지 않는 파일 형식입니다: {original_format}")
    else:
        # ✅ 원본 오디오 파일 변환 (메모리에서 처리)
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=original_format)

        # ✅ MP3로 변환
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")  # 192kbps 고음질 설정
        output_buffer.seek(0)

        # ✅ 변환된 파일 다운로드 버튼 제공
        st.download_button(
            label="🔽 변환된 MP3 파일 다운로드",
            data=output_buffer,
            file_name=f"converted.{DEFAULT_OUTPUT_FORMAT}",
            mime=f"audio/{DEFAULT_OUTPUT_FORMAT}"
        )

st.write("FFmpeg이 정상적으로 실행되는지 확인하려면 [FFmpeg 다운로드 가이드](https://www.gyan.dev/ffmpeg/builds/)를 참고하세요.")
