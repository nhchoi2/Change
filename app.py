import streamlit as st
import io
import mimetypes
import os
from pydub import AudioSegment

# ✅ FFmpeg 경로를 직접 설정 (절대 경로로 변경)
ffmpeg_path = r"C:\Users\nhcho\OneDrive\바탕 화면\Github\Change\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"

# ✅ FFmpeg을 환경 변수에도 추가 (Python 실행 환경에서도 인식되도록)
os.environ["FFMPEG_BINARY"] = ffmpeg_path
AudioSegment.converter = ffmpeg_path

print(f"✅ FFmpeg 경로 설정 완료: {AudioSegment.converter}")


# ✅ 지원하는 입력 포맷
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
    file_extension = uploaded_file.name.split(".")[-1].lower()
    detected_type = mimetypes.guess_type(uploaded_file.name)[0]  # MIME 타입 확인

    st.write(f"🔍 감지된 파일 형식: {detected_type}, 확장자: {file_extension}")

    # ✅ MIME 타입이 `octet-stream`인 경우 AMR로 강제 처리
    if detected_type is None or detected_type == "application/octet-stream":
        detected_type = f"audio/{file_extension}"  # 확장자를 기반으로 MIME 타입 강제 설정

    if file_extension not in SUPPORTED_FORMATS:
        st.error(f"지원되지 않는 파일 형식입니다: {file_extension}")
    else:
        # ✅ 파일 변환 실행
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=file_extension)

        # ✅ MP3로 변환
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format=DEFAULT_OUTPUT_FORMAT, bitrate="192k")
        output_buffer.seek(0)

        # ✅ 변환된 파일 다운로드 버튼 제공
        st.download_button(
            label="🔽 변환된 MP3 파일 다운로드",
            data=output_buffer,
            file_name=f"converted.{DEFAULT_OUTPUT_FORMAT}",
            mime=f"audio/{DEFAULT_OUTPUT_FORMAT}"
        )

st.write("FFmpeg이 정상적으로 실행되는지 확인하려면 [FFmpeg 다운로드 가이드](https://www.gyan.dev/ffmpeg/builds/)를 참고하세요.")
