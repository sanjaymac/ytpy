import streamlit as st
from yt_dlp import YoutubeDL
import pandas as pd
from time import sleep

st.set_page_config(page_title="Profile URL Extractor", layout="wide")

st.title('📱 Bulk Instagram & Facebook Profile URL Extractor')
st.markdown("""
Enter multiple Instagram or Facebook reel URLs (one per line) below, then click **Extract Profile URLs** to get uploader/channel info and profile links.
""")

input_urls = st.text_area(
    "🔗 Enter Instagram or Facebook Reel URLs (one per line):",
    height=250
)

if st.button('🚀 Extract Profile URLs'):
    urls = [url.strip() for url in input_urls.splitlines() if url.strip()]
    
    if not urls:
        st.error("⚠️ Please enter at least one URL.")
    else:
        results = []
        progress_bar = st.progress(0)
        total = len(urls)
        
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'force_generic_extractor': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls, start=1):
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    if 'facebook.com' in url:
                        uploader = info.get('uploader')
                        uploader_id = info.get('uploader_id')
                        uploader_url = info.get('uploader_url')
                        
                        profile_url = (f'https://www.facebook.com/profile.php?id={uploader_id}'
                                       if uploader_id else uploader_url or 'Profile URL not available')
                        
                        results.append({
                            'Platform': 'Facebook',
                            'Input URL': url,
                            'Uploader': uploader,
                            'Uploader ID': uploader_id,
                            'Profile URL': profile_url
                        })
                    
                    elif 'instagram.com' in url:
                        channel = info.get('channel')
                        uploader_url = info.get('uploader_url')
                        
                        profile_url = (f'https://www.instagram.com/{channel}/'
                                       if channel else uploader_url or 'Profile URL not available')
                        
                        results.append({
                            'Platform': 'Instagram',
                            'Input URL': url,
                            'Channel (Username)': channel,
                            'Profile URL': profile_url
                        })
                    else:
                        results.append({
                            'Platform': 'Unknown',
                            'Input URL': url,
                            'Error': 'Unsupported URL'
                        })
                        
                except Exception as e:
                    results.append({
                        'Platform': 'Error',
                        'Input URL': url,
                        'Error': str(e)
                    })
                
                progress_bar.progress(i / total)
                sleep(0.1)  # Slight delay for UX purpose

        progress_bar.empty()
        st.success('✅ Extraction complete!')
        
        df = pd.DataFrame(results)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name='profile_urls.csv',
            mime='text/csv'
        )
