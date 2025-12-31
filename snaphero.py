#!/usr/bin/env python3
"""
SnapHero - A powerful website screenshot utility with advanced features.

Usage:
    python snaphero.py --url https://www.example.com --output output.png --full-page --delay 2
    python snaphero.py --manual                    # Show detailed manual
    python snaphero.py --examples                  # Show usage examples
    python snaphero.py --batch urls.txt            # Batch capture from file

For detailed help, run:
    python snaphero.py --manual
"""

import argparse
import time
import subprocess
import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime

VERSION = "2.0.0"

def show_banner():
    """Display a banner in the terminal using figlet."""
    try:
        subprocess.run(["figlet", "-f", "slant", "SnapHero"], check=True)
        subprocess.run(["figlet", "-f", "small", f"v{VERSION} - by coldman07(vibhu)"], check=True)
    except Exception:
        print(f"=== SnapHero v{VERSION} ===")
        print("Created by coldman07(vibhu)\n")

def show_manual():
    """Display comprehensive manual for SnapHero."""
    manual = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         SNAPHERO - COMPLETE MANUAL                         ║
╚════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
    SnapHero is a powerful command-line tool for capturing website screenshots
    with advanced options including full-page capture, custom viewports, delays,
    quality settings, and batch processing.

BASIC OPTIONS:
    --url URL
        The URL of the webpage to capture (required for single capture)
        Example: --url https://www.example.com

    --output FILE
        Output filename for the screenshot (default: screenshot.png)
        Supports: .png, .jpg, .jpeg
        Example: --output screenshot.png

    --full-page
        Capture the entire scrollable page instead of just viewport
        Example: --full-page

    --delay SECONDS
        Wait time in seconds after page load before capturing
        Useful for dynamic content and animations (default: 0)
        Example: --delay 3

VIEWPORT OPTIONS:
    --viewport-width PIXELS
        Set browser viewport width (default: 1280)
        Example: --viewport-width 1920

    --viewport-height PIXELS
        Set browser viewport height (default: 720)
        Example: --viewport-height 1080

    --mobile
        Use mobile device viewport (375x667)
        Emulates iPhone SE

    --tablet
        Use tablet device viewport (768x1024)
        Emulates iPad

QUALITY OPTIONS:
    --quality LEVEL
        JPEG quality level 1-100 (default: 80)
        Only applies to .jpg/.jpeg files
        Example: --quality 90

    --scale FACTOR
        Device scale factor for higher resolution (default: 1)
        Use 2 for Retina/HiDPI displays
        Example: --scale 2

ADVANCED FEATURES:
    --dark-mode
        Enable dark mode for the page
        Useful for dark theme screenshots

    --hide-cookie-banners
        Attempt to hide common cookie consent banners
        Uses CSS to hide typical banner elements

    --wait-for-selector SELECTOR
        Wait for a specific CSS selector before capturing
        Example: --wait-for-selector "#main-content"

    --timeout MILLISECONDS
        Page load timeout in milliseconds (default: 15000)
        Example: --timeout 30000

    --user-agent STRING
        Custom user agent string
        Example: --user-agent "Mozilla/5.0 Custom Bot"

BATCH PROCESSING:
    --batch FILE
        Capture multiple URLs from a text file (one URL per line)
        Example: --batch urls.txt

    --batch-prefix PREFIX
        Prefix for batch output files (default: "screenshot_")
        Example: --batch-prefix "site_"

INFORMATION:
    --manual
        Display this comprehensive manual

    --examples
        Show practical usage examples

    --version
        Display version information

    -h, --help
        Show quick help message

EXAMPLES:
    See --examples for practical usage examples

NOTES:
    • Requires Playwright to be installed: pip install playwright
    • After installation, run: playwright install chromium
    • Supports PNG and JPEG formats
    • Use --full-page for long pages
    • Add --delay for JavaScript-heavy sites

AUTHOR:
    Created by coldman07(vibhu)
    Version: 2.1
""".format(version=VERSION)
    print(manual)

def show_examples():
    """Display practical usage examples."""
    examples = """
╔════════════════════════════════════════════════════════════════════════════╗
║                        SNAPHERO - USAGE EXAMPLES                           ║
╚════════════════════════════════════════════════════════════════════════════╝

1. BASIC SCREENSHOT:
   python snaphero.py --url https://www.example.com

2. FULL PAGE CAPTURE:
   python snaphero.py --url https://www.example.com --full-page --output full.png

3. MOBILE VIEWPORT:
   python snaphero.py --url https://www.example.com --mobile

4. HIGH-QUALITY SCREENSHOT WITH DELAY:
   python snaphero.py --url https://www.example.com --delay 3 --quality 95 --output high-quality.jpg

5. RETINA DISPLAY (2X RESOLUTION):
   python snaphero.py --url https://www.example.com --scale 2

6. CUSTOM VIEWPORT SIZE:
   python snaphero.py --url https://www.example.com --viewport-width 1920 --viewport-height 1080

7. DARK MODE SCREENSHOT:
   python snaphero.py --url https://www.example.com --dark-mode

8. WAIT FOR SPECIFIC ELEMENT:
   python snaphero.py --url https://www.example.com --wait-for-selector "#content"

9. HIDE COOKIE BANNERS:
   python snaphero.py --url https://www.example.com --hide-cookie-banners --full-page

10. BATCH CAPTURE FROM FILE:
    python snaphero.py --batch urls.txt --batch-prefix "site_" --full-page

11. CUSTOM USER AGENT:
    python snaphero.py --url https://www.example.com --user-agent "CustomBot/1.0"

12. FULL FEATURED CAPTURE:
    python snaphero.py --url https://www.example.com \\
        --output screenshot.png \\
        --full-page \\
        --delay 2 \\
        --viewport-width 1920 \\
        --viewport-height 1080 \\
        --scale 2 \\
        --hide-cookie-banners \\
        --dark-mode

BATCH FILE EXAMPLE (urls.txt):
    https://www.example.com
    https://www.github.com
    https://www.stackoverflow.com

TIP: Use --manual to see all available options and detailed descriptions.
"""
    print(examples)

def capture_screenshot(url, output_file="screenshot.png", full_page=False, delay=0, 
                      viewport_width=1280, viewport_height=720, quality=80, scale=1,
                      dark_mode=False, hide_cookie_banners=False, wait_for_selector=None,
                      timeout=15000, user_agent=None):
    """
    Capture a screenshot of a webpage with advanced options.

    Parameters:
        url (str): The URL of the webpage to capture.
        output_file (str): Filename to save the screenshot.
        full_page (bool): If True, capture the entire scrollable page.
        delay (float): Delay in seconds after page load before capturing.
        viewport_width (int): Width of the browser viewport.
        viewport_height (int): Height of the browser viewport.
        quality (int): JPEG quality level (1-100).
        scale (float): Device scale factor for higher resolution.
        dark_mode (bool): Enable dark mode.
        hide_cookie_banners (bool): Attempt to hide cookie banners.
        wait_for_selector (str): CSS selector to wait for before capturing.
        timeout (int): Page load timeout in milliseconds.
        user_agent (str): Custom user agent string.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context_options = {
            'viewport': {'width': viewport_width, 'height': viewport_height},
            'device_scale_factor': scale
        }
        
        if dark_mode:
            context_options['color_scheme'] = 'dark'
        
        if user_agent:
            context_options['user_agent'] = user_agent
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        try:
            print(f"🌐 Loading {url}...")
            page.goto(url, timeout=timeout)
            
            if wait_for_selector:
                print(f"⏳ Waiting for selector: {wait_for_selector}")
                page.wait_for_selector(wait_for_selector, timeout=timeout)
            
            if hide_cookie_banners:
                print("🍪 Hiding cookie banners...")
                page.evaluate("""
                    const selectors = [
                        '[class*="cookie"]', '[id*="cookie"]',
                        '[class*="consent"]', '[id*="consent"]',
                        '[class*="gdpr"]', '[id*="gdpr"]',
                        '[aria-label*="cookie"]', '[aria-label*="consent"]'
                    ];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            if (el.offsetHeight > 50) el.style.display = 'none';
                        });
                    });
                """)
            
            if delay > 0:
                print(f"⏱️  Waiting {delay} seconds...")
                time.sleep(delay)
            
            screenshot_options = {
                'path': output_file,
                'full_page': full_page
            }
            
            if output_file.lower().endswith(('.jpg', '.jpeg')):
                screenshot_options['type'] = 'jpeg'
                screenshot_options['quality'] = quality
            
            page.screenshot(**screenshot_options)
            file_size = os.path.getsize(output_file)
            print(f"✅ Screenshot saved: {output_file} ({file_size:,} bytes)")
            
        except PlaywrightTimeoutError:
            print(f"❌ Error: Page took too long to load (timeout: {timeout}ms)")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            browser.close()

def batch_capture(file_path, **kwargs):
    """
    Capture screenshots for multiple URLs from a file.

    Parameters:
        file_path (str): Path to file containing URLs (one per line).
        **kwargs: Additional arguments passed to capture_screenshot.
    """
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not urls:
            print("❌ No valid URLs found in file.")
            return
        
        print(f"\n📋 Found {len(urls)} URLs to capture\n")
        prefix = kwargs.pop('batch_prefix', 'screenshot_')
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = url.split('//')[-1].split('/')[0].replace('www.', '')
            output_file = f"{prefix}{domain}_{timestamp}.png"
            
            capture_screenshot(url, output_file=output_file, **kwargs)
        
        print(f"\n🎉 Batch capture complete! Processed {len(urls)} URLs.")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")

def parse_arguments():
    """Parse command-line arguments for SnapHero."""
    parser = argparse.ArgumentParser(
        description="SnapHero - Capture screenshots of web pages with advanced options.",
        epilog="For detailed documentation, use: python snaphero.py --manual",
        add_help=True
    )
    
    # Basic options
    parser.add_argument("--url", help="URL to capture (e.g. https://www.example.com)")
    parser.add_argument("--output", default="screenshot.png", help="Output filename (default: screenshot.png)")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--delay", type=float, default=0, help="Delay after page load in seconds (default: 0)")
    
    # Viewport options
    parser.add_argument("--viewport-width", type=int, default=1280, help="Viewport width (default: 1280)")
    parser.add_argument("--viewport-height", type=int, default=720, help="Viewport height (default: 720)")
    parser.add_argument("--mobile", action="store_true", help="Use mobile viewport (375x667)")
    parser.add_argument("--tablet", action="store_true", help="Use tablet viewport (768x1024)")
    
    # Quality options
    parser.add_argument("--quality", type=int, default=80, help="JPEG quality 1-100 (default: 80)")
    parser.add_argument("--scale", type=float, default=1, help="Device scale factor (default: 1, use 2 for Retina)")
    
    # Advanced features
    parser.add_argument("--dark-mode", action="store_true", help="Enable dark mode")
    parser.add_argument("--hide-cookie-banners", action="store_true", help="Hide cookie consent banners")
    parser.add_argument("--wait-for-selector", help="Wait for CSS selector before capturing")
    parser.add_argument("--timeout", type=int, default=15000, help="Page load timeout in ms (default: 15000)")
    parser.add_argument("--user-agent", help="Custom user agent string")
    
    # Batch processing
    parser.add_argument("--batch", help="Batch capture from file (one URL per line)")
    parser.add_argument("--batch-prefix", default="screenshot_", help="Prefix for batch files (default: screenshot_)")
    
    # Information
    parser.add_argument("--manual", action="store_true", help="Show comprehensive manual")
    parser.add_argument("--examples", action="store_true", help="Show usage examples")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    return parser.parse_args()

def main():
    """Main function to orchestrate SnapHero operations."""
    args = parse_arguments()
    
    # Show version
    if args.version:
        print(f"SnapHero v{VERSION}")
        print("Created by coldman07(vibhu)")
        return
    
    # Show manual
    if args.manual:
        show_manual()
        return
    
    # Show examples
    if args.examples:
        show_examples()
        return
    
    # Display banner
    show_banner()
    
    # Handle mobile/tablet presets
    if args.mobile:
        args.viewport_width = 375
        args.viewport_height = 667
        print("📱 Using mobile viewport (375x667)")
    
    if args.tablet:
        args.viewport_width = 768
        args.viewport_height = 1024
        print("📱 Using tablet viewport (768x1024)")
    
    # Validate quality
    if not 1 <= args.quality <= 100:
        print("❌ Error: Quality must be between 1 and 100")
        sys.exit(1)
    
    # Batch mode
    if args.batch:
        batch_capture(
            args.batch,
            full_page=args.full_page,
            delay=args.delay,
            viewport_width=args.viewport_width,
            viewport_height=args.viewport_height,
            quality=args.quality,
            scale=args.scale,
            dark_mode=args.dark_mode,
            hide_cookie_banners=args.hide_cookie_banners,
            wait_for_selector=args.wait_for_selector,
            timeout=args.timeout,
            user_agent=args.user_agent,
            batch_prefix=args.batch_prefix
        )
        return
    
    # Single capture mode
    if not args.url:
        print("❌ Error: --url is required for single capture mode")
        print("💡 Use --help for usage, --manual for detailed docs, or --examples for examples")
        sys.exit(1)
    
    capture_screenshot(
        url=args.url,
        output_file=args.output,
        full_page=args.full_page,
        delay=args.delay,
        viewport_width=args.viewport_width,
        viewport_height=args.viewport_height,
        quality=args.quality,
        scale=args.scale,
        dark_mode=args.dark_mode,
        hide_cookie_banners=args.hide_cookie_banners,
        wait_for_selector=args.wait_for_selector,
        timeout=args.timeout,
        user_agent=args.user_agent
    )

if __name__ == "__main__":
    main()
