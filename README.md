# LinkedIn Bot with Advanced Stealth Features

This bot automates LinkedIn interactions with sophisticated anti-detection features that mimic human behavior.

## Features

- **Enhanced Stealth Mode**: Uses multiple techniques to avoid bot detection
- **Human-like Behavior**: Realistic mouse movements, typing patterns, and browsing behavior
- **Geolocation Spoofing**: Configurable location settings
- **Browser Fingerprint Protection**: Custom headers, user agent rotation, and WebDriver protection

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Install Playwright browsers:
   ```
   playwright install
   ```
5. Create a `.env` file in the project root with the following variables:
   ```
   EMAIL=your_linkedin_email
   PASSWORD=your_linkedin_password
   AGENTQL_API_KEY=your_agentql_api_key
   ```

## Usage

Run the bot with:

```
python main.py
```

## Anti-Detection Features

- **Browser Configuration**:
  - Disables automation flags
  - Randomizes viewport dimensions
  - Rotates user agents
  - Sets appropriate language and timezone

- **Realistic Human Behavior**:
  - Bezier curve mouse movements
  - Variable typing speeds with natural pauses
  - Randomized scrolling patterns
  - Natural click patterns with slight imprecisions

- **Network & Headers**:
  - Realistic HTTP headers
  - Search engine referrers
  - Cookie management
  - Language settings

- **Location & Identity**:
  - Configurable geolocation (default: Texas area)
  - Timezone matching
  - Consistent browser preferences

## Customization

- Edit user agents in the `USER_AGENTS` list
- Modify geolocation in the `get_geolocation()` function
- Adjust timing parameters in various functions to match your preferences

## Disclaimer

This tool is for educational purposes only. Use of this bot may violate LinkedIn's Terms of Service. Use responsibly and at your own risk.

## License

MIT
