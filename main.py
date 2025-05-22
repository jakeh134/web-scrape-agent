import os
import agentql
import random
import time
import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from env file
load_dotenv()

# Get USER NAME and PASSWORD from env variables
USER_NAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Make sure the AgentQL API key is set
AGENTQL_API_KEY = os.getenv("AGENTQL_API_KEY")
if AGENTQL_API_KEY:
    os.environ["AGENTQL_API_KEY"] = AGENTQL_API_KEY
    print("AgentQL API Key loaded successfully")
else:
    print("Warning: AGENTQL_API_KEY not found in environment variables")

# Initialize AgentQL
agentql.api_key = AGENTQL_API_KEY

# LinkedIn URL with specific parameters
INITIAL_URL = "https://www.linkedin.com/home?locale=en_US"

# Search engine referrers to make it look like we came from a search
SEARCH_REFERRERS = [
    "https://www.google.com/search?q=linkedin+login",
    "https://www.bing.com/search?q=sign+in+to+linkedin",
    "https://duckduckgo.com/?q=linkedin+professional+network",
    "https://www.google.com/search?q=professional+networking+site",
]

# List of popular user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Texas location - Round Rock/Hutto area with slight randomization
def get_geolocation():
    # Base coordinates with slight natural variation
    # LinkedIn would expect small variations even when logging in from the same location
    return {
        "latitude": 30.5706787 + random.uniform(-0.001, 0.001),  # Very small variation (about 100 meters)
        "longitude": -97.5383835 + random.uniform(-0.001, 0.001),
        "accuracy": random.randint(12, 25)  # Realistic GPS accuracy in meters
    }

# Browser viewport settings with slight randomization
def get_viewport_size():
    # Common desktop resolutions with slight variations
    base_sizes = [
        {"width": 1920, "height": 1080},
        {"width": 1680, "height": 1050},
        {"width": 1440, "height": 900},
        {"width": 1366, "height": 768}
    ]
    
    base = random.choice(base_sizes)
    # Add slight variations to look less programmatic
    return {
        "width": base["width"] + random.randint(-5, 5),
        "height": base["height"] + random.randint(-5, 5)
    }

# GraphQL queries
FIND_LOGIN_WITH_EMAIL_BTN_QUERY = """
{
    login_form {
        sign_in_with_email_btn
    }
}
"""

FIND_EMAIL_INPUT_QUERY = """
{
    login_form {
        email_input
        password_input
        sign_in_btn
    }
}
"""

# Global page variable for reference in functions
page = None

# Human-like delays with normal distribution pattern
def wait_human(min_ms=800, max_ms=2000, stddev_factor=0.15):
    # Base delay with slight normal distribution tendency toward middle values
    mean = (min_ms + max_ms) / 2
    stddev = (max_ms - min_ms) * stddev_factor
    delay = int(random.normalvariate(mean, stddev))
    
    # Ensure we stay within our bounds
    delay = max(min_ms, min(max_ms, delay))
    
    # Occasionally add a micro-pause for more realism
    if random.random() < 0.1:
        micro_pause = random.randint(10, 80)
        delay += micro_pause
    
    if page:  # Make sure page exists
        page.wait_for_timeout(delay)
    else:
        time.sleep(delay / 1000)  # Convert ms to seconds

# More realistic mouse movements with bezier curve-like paths
def realistic_mouse_movement(start_x=None, start_y=None, end_x=None, end_y=None, steps=None):
    if not page:
        return
        
    # Get current mouse position if not specified
    if start_x is None or start_y is None:
        # Assume middle of screen if we don't know current position
        start_x = page.viewport_size["width"] // 2
        start_y = page.viewport_size["height"] // 2
    
    # Generate random end point if not specified
    if end_x is None or end_y is None:
        end_x = random.randint(100, page.viewport_size["width"] - 100)
        end_y = random.randint(100, page.viewport_size["height"] - 100)
    
    # Random number of steps if not specified (more steps = smoother)
    if steps is None:
        # Calculate distance-based steps with randomization
        distance = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        steps = int(max(5, min(25, distance / 20))) + random.randint(-2, 5)
    
    # Generate control points for bezier-like movement
    # Simple approximation of a curve by generating midpoints with randomness
    control_x1 = start_x + (end_x - start_x) * random.uniform(0.2, 0.4)
    control_y1 = start_y + (end_y - start_y) * random.uniform(0.2, 0.8)
    control_x2 = start_x + (end_x - start_x) * random.uniform(0.6, 0.8)
    control_y2 = start_y + (end_y - start_y) * random.uniform(0.2, 0.8)
    
    for i in range(steps + 1):
        t = i / steps
        # Cubic bezier formula (simplified)
        x = (1-t)**3 * start_x + 3*(1-t)**2 * t * control_x1 + 3*(1-t) * t**2 * control_x2 + t**3 * end_x
        y = (1-t)**3 * start_y + 3*(1-t)**2 * t * control_y1 + 3*(1-t) * t**2 * control_y2 + t**3 * end_y
        
        # Add small random jitter to simulate human hand movement
        if 0 < i < steps:
            x += random.normalvariate(0, 1)
            y += random.normalvariate(0, 1)
        
        # Move to this point
        page.mouse.move(x, y)
        
        # Small random delay between movements
        delay = random.randint(5, 15)
        if random.random() < 0.1:  # Occasionally pause slightly longer
            delay += random.randint(30, 80)
            page.wait_for_timeout(delay)

# Enhanced random scrolling to simulate human page exploration
def random_scroll():
    if not page:
        return
        
    # Determine scroll direction probability (down more common than up)
    scroll_down = random.random() < 0.7
    
    # Determine scroll type
    scroll_type = random.random()
    
    # Occasional small scroll (as if reading text)
    if scroll_type < 0.6:
        distance = random.randint(100, 300) * (-1 if not scroll_down else 1)
        # Smooth scrolling with multiple smaller steps
        steps = random.randint(3, 8)
        for _ in range(steps):
            step_distance = distance // steps
            page.mouse.wheel(0, step_distance)
            page.wait_for_timeout(random.randint(30, 80))
    
    # Medium scroll (moving to next section)
    elif scroll_type < 0.9:
        distance = random.randint(300, 700) * (-1 if not scroll_down else 1)
        page.mouse.wheel(0, distance)
        
    # Occasional large scroll (skimming page)
    else:
        distance = random.randint(700, 1200) * (-1 if not scroll_down else 1)
        page.mouse.wheel(0, distance)
    
    wait_human(300, 800)

# Human-like typing with random pauses and occasional corrections
def human_type(element, text):
    if not element:
        print("Error: element not found for typing")
        return

    element.click()
    
    # Split text into chunks to simulate thinking while typing
    if len(text) > 10 and random.random() < 0.3:
        split_point = random.randint(len(text) // 3, len(text) * 2 // 3)
        chunks = [text[:split_point], text[split_point:]]
    else:
        chunks = [text]
    
    for chunk in chunks:
        # Typing speed varies for different people, adjust range as needed
        try:
        # Use fixed delay instead of lambda function to avoid serialization issues
            base_delay = random.uniform(50, 150)
            element.press_sequentially(chunk, delay=base_delay)
        except Exception as e:
            print(f"Error in press_sequentially: {e}")
        # Fall back to fill method
        element.fill(chunk)
        
        # Occasionally pause while typing as if thinking
        if len(chunks) > 1 and chunk != chunks[-1]:
            page.wait_for_timeout(random.randint(300, 1200))
    
    # Sometimes click away and come back before submitting
    if random.random() < 0.15:
        # Click elsewhere
        page.mouse.click(
        random.randint(100, page.viewport_size["width"] - 100),
        random.randint(100, page.viewport_size["height"] - 100)
        )
        wait_human(300, 800)
        element.click()
        wait_human(200, 500)

# Realistic human-like clicking
def human_click(element, double_click_probability=0.01):
    if not element:
        print("Error: element not found for clicking")
        return
        
    # Get element's bounding box
    box = element.bounding_box()
    
    if not box:
        # Fallback if we can't get bounding box
        element.click()
        return
        
    # Move to the element with realistic mouse movement
    realistic_mouse_movement(
        end_x=box['x'] + box['width'] * random.uniform(0.2, 0.8),
        end_y=box['y'] + box['height'] * random.uniform(0.2, 0.8)
    )
    
    # Slight pause before clicking (as humans do)
    wait_human(50, 150)
    
    # 1% chance of accidental double-click (happens to humans)
    if random.random() < double_click_probability:
        page.mouse.dblclick(
        box['x'] + box['width'] * random.uniform(0.2, 0.8),
        box['y'] + box['height'] * random.uniform(0.2, 0.8)
        )
    else:
        page.mouse.click(
        box['x'] + box['width'] * random.uniform(0.2, 0.8),
        box['y'] + box['height'] * random.uniform(0.2, 0.8)
        )

# Random human-like behaviors to perform periodically
def perform_random_behaviors(chance=0.7):
    if not page or random.random() >= chance:
        return
        
    behaviors = [
        lambda: realistic_mouse_movement(),
        lambda: random_scroll(),
        lambda: wait_human(1000, 3000),  # Sometimes just pause
        lambda: page.wait_for_timeout(random.randint(100, 300))  # Micro pause
    ]
    
    # Choose 1-3 random behaviors
    num_behaviors = random.randint(1, 3)
    for _ in range(num_behaviors):
        random.choice(behaviors)()

# Global variables to store browser resources
browser = None
context = None
playwright_instance = None

# Login execution
def login(playwright):
    global page, browser, context  # Use the global page variable
    
    # Custom browser arguments
    browser_args = [
        "--lang=en-US",  # Force English language
        "--disable-blink-features=AutomationControlled",  # Disable automation flags
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials", 
        "--no-sandbox",
        "--disable-infobars", 
        "--no-default-browser-check",
        f"--window-size={get_viewport_size()['width']},{get_viewport_size()['height']}",
        "--disable-extensions",
        "--disable-plugins-discovery",
        "--disable-automation",
        "--no-first-run",
        "--no-service-autorun",
        "--password-store=basic",
        "--use-mock-keychain",
        "--user-agent=" + "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    try:
            # Launch browser with custom arguments
        browser = playwright.chromium.launch(
        headless=False,
        args=browser_args
        )
        
        # Browser context with additional options
        context = browser.new_context(
            viewport=get_viewport_size(),
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            geolocation=get_geolocation(),
            locale="en-US",
            timezone_id="America/Chicago",
            color_scheme="no-preference",
            reduced_motion="no-preference",
            has_touch=False,
            is_mobile=False,
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            # Enhanced HTTP headers
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "sec-ch-ua": "\"Google Chrome\";v=\"120\", \"Chromium\";v=\"120\", \"Not-A.Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "Referer": random.choice(SEARCH_REFERRERS),
            }
        )
        
        # Create standard page first, so we can do initial navigation
        standard_page = context.new_page()
        
        # Set global page for use in functions
        page = standard_page
        
        # Set cookies that a normal browser would have
        page.context.add_cookies([
            {
                "name": "li_at", 
                "value": "", # Empty for now
                "domain": ".linkedin.com", 
                "path": "/"
            }
        ])
        
        # Initial page load with search engine referrer
        print("Loading initial page...")
        page.goto(INITIAL_URL)
        wait_human(1000, 2500)  # Random delay after page load
        
        # Now wrap with AgentQL after basic setup and initial page load is done
        print("Setting up AgentQL...")
        try:
            agentql_page = agentql.wrap(page)
            # Reassign global page variable
            page = agentql_page
            
            # Enable stealth mode to avoid bot detection
            print("Enabling stealth mode...")
            page.enable_stealth_mode()
        except Exception as e:
            print(f"Error setting up AgentQL: {e}")
            # Continue with standard page if AgentQL fails
            print("Continuing with standard Playwright page...")
        
        # Random behaviors after page load to simulate a human looking at the page
        for _ in range(random.randint(2, 4)):
            realistic_mouse_movement()
            wait_human(500, 1200)
        
        random_scroll()

        # Use query_elements() method to locate "Sign in with email" button
        print("Finding sign-in button...")
        try:
            response = page.query_elements(FIND_LOGIN_WITH_EMAIL_BTN_QUERY)
            if not response or not hasattr(response, 'login_form') or not hasattr(response.login_form, 'sign_in_with_email_btn'):
                print("Could not find sign in with email button, trying standard selector")
                sign_in_btn = page.locator("button:has-text('Sign in with email')")
                if sign_in_btn.count() > 0:
                    print("Found sign-in button using standard selector")
                    # More random behaviors before clicking
                    perform_random_behaviors()
                    wait_human(500, 1200)  # Random delay before clicking
                    
                    # Click on Sign in with email button
                    print("Clicking sign-in with email button...")
                    sign_in_btn.click()
                else:
                    raise Exception("Could not find any sign in button")
            else:
                # More random behaviors before clicking
                perform_random_behaviors()
                wait_human(500, 1200)  # Random delay before clicking
                
                # Click on Sign in with email button using human-like click
                print("Clicking sign-in with email button...")
                human_click(response.login_form.sign_in_with_email_btn)
        except Exception as e:
            print(f"Error finding sign-in button: {e}")
            sign_in_btn = page.locator("button:has-text('Sign in with email')")
            if sign_in_btn.count() > 0:
                print("Found sign-in button using standard selector after error")
                sign_in_btn.click()
            else:
                raise Exception("Could not find any sign in button after error")

        # Random delay after clicking and before filling form
        wait_human(1000, 2500)
        perform_random_behaviors(0.5)  # 50% chance of random behaviors
        
        # Login with email
        print("Finding email and password inputs...")
        try:
            response = page.query_elements(FIND_EMAIL_INPUT_QUERY)
            if not response or not hasattr(response, 'login_form'):
                print("Could not find login form elements using query, trying standard selectors")
                email_input = page.locator("input[type='email'], input[name='email'], input#username")
                password_input = page.locator("input[type='password'], input[name='password']")
                
                if email_input.count() > 0 and password_input.count() > 0:
                    print("Found login form using standard selectors")
                    
                    # Use standard Playwright interactions
                    print("Typing email address...")
                    email_input.fill(USER_NAME)
                    
                    wait_human(800, 1500)  # Pause between email and password fields
                    perform_random_behaviors(0.3)  # 30% chance of random behaviors
                    
                    print("Typing password...")
                    password_input.fill(PASSWORD)
                    
                    # Uncheck "Remember me" checkbox if it exists
                    remember_me = page.locator("input[type='checkbox']#remember-me, label:has-text('Remember me'), input[name='remember-me']")
                    if remember_me.count() > 0:
                        print("Found 'Remember me' checkbox - ensuring it's unchecked")
                        if remember_me.is_checked():
                            remember_me.uncheck()
                    
                    # Find submit button - be more specific to avoid multiple matches
                    submit_btn = page.locator("button[type='submit'][data-litms-control-urn='login-submit'], button.btn__primary--large")
                    wait_human(1200, 2500)
                    
                    if submit_btn.count() > 0:
                        # First option - click with strict=false
                        try:
                            submit_btn.click(strict=False)
                        except Exception as e:
                            print(f"Error clicking submit button: {e}")
                            # Second option - try using first element
                            submit_btn.first.click()
                    else:
                        password_input.press("Enter")
                else:
                    raise Exception("Could not find email/password inputs with standard selectors")
            else:
                # Use human-like typing with random delays
                print("Typing email address...")
                try:
                    human_type(response.login_form.email_input, USER_NAME)
                except Exception as e:
                    print(f"Error with human_type for email: {e}")
                    # Fall back to standard fill
                    response.login_form.email_input.fill(USER_NAME)
                
                wait_human(800, 1500)  # Pause between email and password fields
                perform_random_behaviors(0.3)  # 30% chance of random behaviors
                
                print("Typing password...")
                try:
                    human_type(response.login_form.password_input, PASSWORD)
                except Exception as e:
                    print(f"Error with human_type for password: {e}")
                    # Fall back to standard fill
                    response.login_form.password_input.fill(PASSWORD)
                
                # Uncheck "Remember me" checkbox if it exists
                remember_me = page.locator("input[type='checkbox']#remember-me, label:has-text('Remember me'), input[name='remember-me']")
                if remember_me.count() > 0:
                    print("Found 'Remember me' checkbox - ensuring it's unchecked")
                    if remember_me.is_checked():
                        remember_me.uncheck()
                
                # Longer delay before clicking sign in - humans often pause here
                wait_human(1200, 2500)
                perform_random_behaviors(0.6)  # 60% chance of random behaviors
                
                # Click on Sign in button using human-like click
                print("Clicking sign-in button...")
                human_click(response.login_form.sign_in_btn)
        except Exception as e:
            print(f"Error with login form: {e}")
            # Fallback to standard selectors if AgentQL query fails
            email_input = page.locator("input[type='email'], input[name='email'], input#username")
            password_input = page.locator("input[type='password'], input[name='password']")
            
            if email_input.count() > 0 and password_input.count() > 0:
                print("Found login form elements after error")
                email_input.fill(USER_NAME)
                wait_human(800, 1500)
                password_input.fill(PASSWORD)
                
                # Uncheck "Remember me" checkbox if it exists
                remember_me = page.locator("input[type='checkbox']#remember-me, label:has-text('Remember me'), input[name='remember-me']")
                if remember_me.count() > 0:
                    print("Found 'Remember me' checkbox - ensuring it's unchecked")
                    if remember_me.is_checked():
                        remember_me.uncheck()
                
                # Find submit button - be more specific to avoid multiple matches
                submit_btn = page.locator("button[type='submit'][data-litms-control-urn='login-submit'], button.btn__primary--large")
                wait_human(1200, 2500)
                
                if submit_btn.count() > 0:
                    # First option - click with strict=false
                    try:
                        submit_btn.click(strict=False)
                    except Exception as e:
                        print(f"Error clicking submit button: {e}")
                        # Second option - try using first element
                        submit_btn.first.click()
                else:
                    password_input.press("Enter")
            else:
                raise Exception("Could not find login form after error")

        # Wait longer after signing in to simulate page loading/processing time
        wait_human(3000, 5000)
        
        # Final random behaviors after successful login to simulate browsing
        for _ in range(random.randint(3, 5)):
            perform_random_behaviors(0.8)  # 80% chance of random behaviors
            wait_human(800, 2000)
        
        # Allow time to see the result before closing
        print("Script completed successfully. Waiting before closing...")
        page.wait_for_timeout(100000)
        
        # Return the browser, context, and page for use in other functions
        return browser, context, page
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

# Global variables to store browser resources
browser = None
context = None
playwright_instance = None

def init_playwright():
    """Initialize playwright and keep it running throughout the script."""
    global playwright_instance
    playwright_instance = sync_playwright().start()
    return playwright_instance

def main():
    """Main function that keeps the browser open."""
    global playwright_instance, browser, context, page

    # Initialize playwright without context manager to keep it running
    playwright_instance = init_playwright()
    
    try:
        # Call login with our persistent playwright instance
        login_result = login_with_persistent_browser(playwright_instance)
        
        if login_result:
            print("Login successful - browser remains open for further operations")
        
        # Keep script running until user input
        try:
            input("Press Enter to exit the script (browser will remain open until then)...")
        except KeyboardInterrupt:
            print("\nScript terminated by user")
        else:
            print("Login failed")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def login_with_persistent_browser(playwright):
    """Login function that uses a persistent playwright instance."""
    global browser, context, page
    
    # Custom browser arguments
    browser_args = [
        "--lang=en-US",  # Force English language
        "--disable-blink-features=AutomationControlled",  # Disable automation flags
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials", 
        "--no-sandbox",
        "--disable-infobars", 
        "--no-default-browser-check",
        f"--window-size={get_viewport_size()['width']},{get_viewport_size()['height']}",
        "--disable-extensions",
        "--disable-plugins-discovery",
        "--disable-automation",
        "--no-first-run",
        "--no-service-autorun",
        "--password-store=basic",
        "--use-mock-keychain",
        "--user-agent=" + "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    try:
        # Launch browser with custom arguments
        browser = playwright.chromium.launch(
        headless=False,
        args=browser_args
        )
        
        # Rest of login code will run in login() but use our persistent browser
        return login(playwright)
    except Exception as e:
        print(f"Error setting up browser: {e}")
        return False

# Call the main function when running the script directly
    # main()  # Commented out to avoid running both mains
    feed_search()
    
    
URL = "https://www.linkedin.com/feed/"

FIND_MAIN_NAV_QUERY = """
{
    main_nav {
        global_nav_typeahead
    }
}
"""
    
def feed_search():
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
        # Always run login directly
        print("Running fresh login...")
        login(playwright)
        
        page.goto(URL)
        page.wait_for_timeout(100000)

        main_nav_response = page.query_elements(FIND_MAIN_NAV_QUERY)
        # Search for a random user
        random_user = "Ryan Farley"
        main_nav_response.main_nav.global_nav_typeahead.fill(random_user)
        main_nav_response.main_nav.global_nav_typeahead.press("Enter")

        page.wait_for_timeout(100000)

if __name__ == "__main__":
    feed_search()
