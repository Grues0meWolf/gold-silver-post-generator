# 🥇 Gold & Silver News Post Generator

An automated social media content creation tool that fetches articles from Google Alerts RSS feeds and generates beautiful 4:3 social media posts with captions.

## Features

- 📰 **Article Fetching** - Automatically pulls articles from your Google Alerts RSS feed
- 🎨 **Image Generation** - Creates 4:3 social media images (1200x900px) with customizable backgrounds
- ✏️ **Caption Creation** - Generates engaging captions (max 2 paragraphs) for each article
- ☁️ **Cloud Storage** - Automatically uploads images to Google Drive
- 📊 **Tracking** - Logs all posts to Google Sheets for easy management
- 👀 **Preview & Edit** - Review and edit captions before posting

## Deployment Instructions

### Deploy to Streamlit Cloud (Recommended)

1. **Fork or Clone this Repository**
   - Create a GitHub repository with these files
   - Push the code to your GitHub account

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"

3. **Configure the App**
   - Select your repository
   - Set the main file path: `app.py`
   - Click "Deploy"

4. **Set Up Secrets**
   - In Streamlit Cloud, go to your app settings
   - Click on "Secrets"
   - Add the following configuration:

```toml
# RSS Feed Configuration
rss_feed_url = "YOUR_GOOGLE_ALERTS_RSS_FEED_URL"

# Google Sheets Configuration
google_sheet_id = "YOUR_GOOGLE_SHEET_ID"

# Google Drive Configuration
drive_folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"

# Google API Credentials
[google_credentials]
token = "YOUR_GOOGLE_OAUTH_TOKEN"
refresh_token = "YOUR_GOOGLE_REFRESH_TOKEN"
token_uri = "https://oauth2.googleapis.com/token"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
```

### Getting Your Configuration Values

#### RSS Feed URL
- Your Google Alerts RSS feed URL (already provided)

#### Google Sheet ID
- From your Google Sheets URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
- Extract the `SHEET_ID` part

#### Google Drive Folder ID
- From your Google Drive folder URL: `https://drive.google.com/drive/folders/FOLDER_ID`
- Extract the `FOLDER_ID` part

#### Google OAuth Credentials
You need to set up Google OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API and Google Sheets API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON
6. Use the OAuth 2.0 Playground to get your tokens:
   - Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
   - Select Drive API v3 and Sheets API v4
   - Authorize and get your tokens

## Usage

1. **Fetch Articles**
   - Click "Fetch Latest Articles" in the sidebar
   - Browse the articles that appear

2. **Select Articles**
   - Check the boxes next to articles you want to create posts for
   - You can select multiple articles

3. **Generate Content**
   - Go to the "Generate Content" tab
   - Click "Generate Images & Captions"
   - Wait for the processing to complete

4. **Review & Edit**
   - Preview the generated images and captions
   - Edit captions as needed
   - Copy captions for posting

5. **View History**
   - Check the "History" tab for links to your Google Sheets and Drive
   - All generated content is automatically saved

## Customization

### Change Background Color
- Use the color picker in the sidebar to customize the image background

### Modify Caption Style
- Edit the `generate_caption()` function in `app.py`
- Customize hashtags, formatting, and length

### Adjust Image Size
- Modify the `width` and `height` variables in `create_post_image()`
- Current default: 1200x900 (4:3 ratio)

## Tech Stack

- **Frontend**: Streamlit
- **Image Processing**: Pillow (PIL)
- **RSS Parsing**: feedparser
- **Cloud Storage**: Google Drive API
- **Data Tracking**: Google Sheets API

## Support

For issues or questions:
- Check the Streamlit Cloud logs
- Verify your secrets are configured correctly
- Ensure Google API credentials have proper permissions

## License

MIT License - Feel free to use and modify for your needs!

---

**Built with ❤️ for Gold & Silver News**  
*Version 1.0 | October 2025*
