import streamlit as st
import feedparser
import requests
from datetime import datetime
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from PIL import Image, ImageDraw, ImageFont
import base64

# Page config
st.set_page_config(
    page_title="Gold & Silver News Post Generator",
    page_icon="🥇",
    layout="wide"
)

# Load configuration from Streamlit secrets
try:
    RSS_FEED_URL = st.secrets["rss_feed_url"]
    GOOGLE_SHEET_ID = st.secrets["google_sheet_id"]
    DRIVE_FOLDER_ID = st.secrets["drive_folder_id"]
except Exception as e:
    st.error("⚠️ Configuration not found. Please set up your secrets in Streamlit Cloud.")
    st.stop()

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'selected_articles' not in st.session_state:
    st.session_state.selected_articles = set()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}

def get_google_creds():
    """Load Google Drive credentials from Streamlit secrets"""
    try:
        # Get credentials from secrets
        creds_dict = st.secrets["google_credentials"]
        creds = Credentials.from_authorized_user_info(creds_dict)
        return creds
    except Exception as e:
        st.error(f"Error loading Google credentials: {e}")
        return None

def fetch_articles():
    """Fetch articles from RSS feed"""
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        articles = []
        
        for entry in feed.entries[:20]:  # Get last 20 articles
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', 'N/A'),
                'summary': entry.get('summary', '')
            })
        
        return articles
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
        return []

def generate_caption(article_title, article_summary):
    """Generate a caption for the article"""
    # Extract key information
    summary_text = article_summary[:300] if len(article_summary) > 300 else article_summary
    
    # Create caption
    caption = f"📰 {article_title}\n\n"
    caption += f"{summary_text}...\n\n"
    caption += "#Gold #Silver #PreciousMetals #Investment #Finance"
    
    return caption

def create_post_image(article_title, bg_color="#1a1a2e"):
    """Create a 4:3 social media post image"""
    try:
        # Create a 4:3 image (1200x900)
        width, height = 1200, 900
        
        # Create gradient background
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            try:
                # Try alternative font paths for different systems
                title_font = ImageFont.truetype("arial.ttf", 60)
            except:
                title_font = ImageFont.load_default()
        
        # Add title text (wrapped)
        words = article_title.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] > width - 100:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text centered
        y_offset = height // 2 - (len(lines) * 70) // 2
        for line in lines[:3]:  # Max 3 lines
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='white', font=title_font)
            y_offset += 70
        
        return img
    except Exception as e:
        st.error(f"Error creating image: {e}")
        return None

def upload_to_drive(image, filename, creds):
    """Upload image to Google Drive"""
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Save image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        file_metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }
        
        media = MediaIoBaseUpload(img_byte_arr, mimetype='image/png')
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error uploading to Drive: {e}")
        return None

def log_to_sheet(article, caption, image_url, creds):
    """Log the post to Google Sheets"""
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        values = [[
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            article['title'],
            article['link'],
            caption,
            image_url,
            "Generated"
        ]]
        
        body = {'values': values}
        
        service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Sheet1!A:F',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Error logging to sheet: {e}")
        return False

# Main UI
st.title("🥇 Gold & Silver News Post Generator")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    if st.button("🔄 Fetch Latest Articles", use_container_width=True):
        with st.spinner("Fetching articles..."):
            st.session_state.articles = fetch_articles()
            st.success(f"Fetched {len(st.session_state.articles)} articles!")
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Articles Loaded", len(st.session_state.articles))
    st.metric("Selected", len(st.session_state.selected_articles))
    st.metric("Generated", len(st.session_state.generated_content))
    
    st.markdown("---")
    st.markdown("### 🎨 Settings")
    bg_color = st.color_picker("Background Color", "#1a1a2e")

# Main content area
tab1, tab2, tab3 = st.tabs(["📰 Articles", "✨ Generate Content", "📋 History"])

with tab1:
    st.header("Select Articles")
    
    if not st.session_state.articles:
        st.info("👆 Click 'Fetch Latest Articles' in the sidebar to get started!")
    else:
        for idx, article in enumerate(st.session_state.articles):
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                selected = st.checkbox("", key=f"select_{idx}", value=idx in st.session_state.selected_articles)
                if selected:
                    st.session_state.selected_articles.add(idx)
                else:
                    st.session_state.selected_articles.discard(idx)
            
            with col2:
                with st.expander(f"**{article['title']}**"):
                    st.write(f"**Published:** {article['published']}")
                    st.write(f"**Link:** {article['link']}")
                    if article['summary']:
                        st.write(f"**Summary:** {article['summary'][:300]}...")

with tab2:
    st.header("Generate Content")
    
    if not st.session_state.selected_articles:
        st.warning("⚠️ Please select at least one article from the Articles tab")
    else:
        st.success(f"✅ {len(st.session_state.selected_articles)} article(s) selected")
        
        if st.button("🎨 Generate Images & Captions", use_container_width=True, type="primary"):
            creds = get_google_creds()
            
            if not creds:
                st.error("❌ Google Drive credentials not found. Please configure your Google credentials in Streamlit secrets.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, idx in enumerate(st.session_state.selected_articles):
                    article = st.session_state.articles[idx]
                    status_text.text(f"Processing: {article['title'][:50]}...")
                    
                    # Generate caption
                    caption = generate_caption(article['title'], article['summary'])
                    
                    # Create image
                    image = create_post_image(article['title'], bg_color)
                    
                    if image:
                        # Upload to Drive
                        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}.png"
                        image_url = upload_to_drive(image, filename, creds)
                        
                        if image_url:
                            # Log to sheet
                            log_to_sheet(article, caption, image_url, creds)
                            
                            # Store in session
                            st.session_state.generated_content[idx] = {
                                'article': article,
                                'caption': caption,
                                'image': image,
                                'image_url': image_url
                            }
                    
                    progress_bar.progress((i + 1) / len(st.session_state.selected_articles))
                
                status_text.text("✅ All content generated!")
                st.balloons()
        
        # Display generated content
        if st.session_state.generated_content:
            st.markdown("---")
            st.subheader("📱 Preview & Edit")
            
            for idx, content in st.session_state.generated_content.items():
                with st.container():
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.image(content['image'], use_container_width=True)
                        st.caption(f"[View in Drive]({content['image_url']})")
                    
                    with col2:
                        st.markdown(f"**{content['article']['title']}**")
                        edited_caption = st.text_area(
                            "Caption (editable)",
                            value=content['caption'],
                            height=200,
                            key=f"caption_{idx}"
                        )
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📋 Copy Caption", key=f"copy_{idx}"):
                                st.code(edited_caption)
                        with col_b:
                            if st.button("🗑️ Remove", key=f"remove_{idx}"):
                                del st.session_state.generated_content[idx]
                                st.rerun()
                    
                    st.markdown("---")

with tab3:
    st.header("📋 Post History")
    
    if GOOGLE_SHEET_ID:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
        st.info(f"📊 [View your post history in Google Sheets]({sheet_url})")
    
    if DRIVE_FOLDER_ID:
        drive_url = f"https://i.ytimg.com/vi/6NhXHbQOO9o/sddefault.jpg"
        st.info(f"📁 [View your images in Google Drive]({drive_url})")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Made with ❤️ for Gold & Silver News</p>
    <p style='font-size: 0.8em;'>Powered by Streamlit | Version 1.0</p>
</div>
""", unsafe_allow_html=True)
