#!/usr/bin/env python3
"""
SnapHero - A powerful website screenshot utility.

Usage:
    python snaphero.py --url https://www.example.com --output output.png --full-page --delay 2 --viewport-width 1280 --viewport-height 720

Options:
    --url              URL to capture (e.g. https://www.example.com)
    --output           Output file name for the screenshot (default: screenshot.png)
    --full-page        Capture the entire scrollable page
    --delay            Delay (in seconds) after page load before capturing (default: 0)
    --viewport-width   Width of the browser viewport (default: 1280)
    --viewport-height  Height of the browser viewport (default: 720)

For detailed help, run:
    python snaphero.py -h
"""

import argparse
import time
import subprocess
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def show_banner():
    """
    Display a banner in the terminal using figlet.
    """
    try:
        subprocess.run(["figlet", "-f", "slant", "SnapHero"], check=True)
        subprocess.run(["figlet", "-f", "small", "created by coldman07(vibhu)"], check=True)
    except Exception as e:
        print("Figlet not found or an error occurred while generating the banner.")

def capture_screenshot(url, output_file="screenshot.png", full_page=False, delay=0, viewport_width=1280, viewport_height=720):
    """
    Capture a screenshot of a webpage.

    Parameters:
        url (str): The URL of the webpage to capture.
        output_file (str): Filename to save the screenshot (default: "screenshot.png").
        full_page (bool): If True, capture the entire scrollable page.
        delay (float): Delay in seconds after page load before capturing.
        viewport_width (int): Width of the browser viewport.
        viewport_height (int): Height of the browser viewport.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})
        try:
            page.goto(url, timeout=15000)  # 15 seconds timeout
            if delay > 0:
                time.sleep(delay)
            page.screenshot(path=output_file, full_page=full_page)
            print(f"🎉 Screenshot saved as {output_file}")
        except PlaywrightTimeoutError:
            print("Error: Page took too long to load.")
        finally:
            browser.close()

def parse_arguments():
    """
    Parse command-line arguments for SnapHero.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="SnapHero - Capture screenshots of web pages with advanced options.",
        epilog="Example: python snaphero.py --url https://www.example.com --output output.png --full-page --delay 2 --viewport-width 1280 --viewport-height 720"
    )
    parser.add_argument("--url", required=True, help="URL to capture (e.g. https://www.example.com)")
    parser.add_argument("--output", default="screenshot.png", help="Output file name (default: screenshot.png)")
    parser.add_argument("--full-page", action="store_true", help="Capture the full scrollable page")
    parser.add_argument("--delay", type=float, default=0, help="Delay (in seconds) after page load before capturing (default: 0)")
    parser.add_argument("--viewport-width", type=int, default=1280, help="Viewport width (default: 1280)")
    parser.add_argument("--viewport-height", type=int, default=720, help="Viewport height (default: 720)")
    return parser.parse_args()

def main():
    """
    Main function to display banner, parse arguments, and capture the screenshot.
    """
    show_banner()
    args = parse_arguments()
    capture_screenshot(
        url=args.url,
        output_file=args.output,
        full_page=args.full_page,
        delay=args.delay,
        viewport_width=args.viewport_width,
        viewport_height=args.viewport_height
    )

if __name__ == "__main__":
    main()
