import streamlit as st
import streamlit as st
import yt_dlp
from pydub import AudioSegment
import io
import os

st.set_page_config(page_title="Ultimate YT Splitter", layout="wide")

st.title("🎵 Smart Music Splitter")
st.write("Automatically detects chapters and provides loopable controls.")

url = st.text_input("YouTube URL", placeholder="Paste link here...")

def get_video_info(link):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(link, download=False)

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'temp_audio.%(ext)s',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    return "temp_audio.mp3"

if url:
    try:
        info = get_video_info(url)
        chapters = info.get('chapters', [])
        
        if not chapters:
            st.warning("No chapters found. Using manual segmenting (0-30s).")
            chapters = [{'title': 'Full/Manual Start', 'start_time': 0, 'end_time': 30}]

        if st.button("🚀 Process Audio"):
            with st.spinner("Extracting high-quality audio..."):
                file_path = download_audio(url)
                full_audio = AudioSegment.from_file(file_path)
                
                st.divider()
                # Create a grid for the chapters
                cols = st.columns(2)
                
                for i, chap in enumerate(chapters):
                    with cols[i % 2]:
                        name = chap.get('title', f'Part {i+1}')
                        start = int(chap['start_time']) * 1000
                        end = int(chap['end_time']) * 1000
                        
                        # Slice audio
                        segment = full_audio[start:end]
                        buffer = io.BytesIO()
                        segment.export(buffer, format="mp3")
                        
                        st.write(f"### {name}")
                        loop_on = st.toggle("Enable Loop", key=f"loop_{i}")
                        
                        # Streamlit 2025/26 native loop support
                        st.audio(buffer, format="audio/mp3", loop=loop_on)
                
                os.remove(file_path)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
