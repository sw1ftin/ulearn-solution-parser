import requests
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
auth_token = os.getenv("ulearn.auth")

# ==========================================
# YOUR VALUES HERE
course = "ml"
file_extension = "py"

headless = True
timeout = 2000          # 2s, change if not enough to parse code from page
# ==========================================

if not os.path.exists("solutions"):
    os.mkdir("solutions")

link = f"https://ulearn.me/courses/{course}"
course_link = f"https://ulearn.me/course/{course}"
api_link = f"https://api.ulearn.me/courses/{course}"

response = requests.get(api_link)
data = json.loads(response.text)

title = data["title"]
id = data["id"]
units = data["units"]

if not os.path.exists(f"solutions/{id}"):
    os.mkdir(f"solutions/{id}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context()
    context.add_cookies(
        [
            {
                "name": "ulearn.auth",
                "value": auth_token,
                "domain": "ulearn.me",
                "path": "/",
            }
        ]
    )
    page = context.new_page()
    for num_unit, unit in enumerate(units):
        print(f"\n\t==== Unit: {num_unit + 1}/{len(units)} ====")
        if not os.path.exists(f"solutions/{id}/{unit['title']}"):
            os.mkdir(f"solutions/{id}/{unit['title']}")
        slides = unit["slides"]
        for num, slide in enumerate(slides):
            print(f"\t--- Slide: {num + 1}/{len(slides)} ---")
            print(f'Parsing "{slide["title"]}"...')
            page.goto(f"{course_link}/{slide['slug']}")
            try:
                page.wait_for_selector(".CodeMirror", timeout=timeout)
                code = page.evaluate(
                    "() => { const cms = document.querySelectorAll('.CodeMirror'); const last = cms[cms.length - 1]; return last.CodeMirror.getValue(); }"
                )
                with open(
                    f"solutions/{id}/{unit['title']}/{slide['title']}.{file_extension}",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(code)
                print(
                    f'Saved "{slide["title"]}.{file_extension}" in "solutions/{id}/{unit["title"]}/"'
                )
            except Exception:
                print('No code found')
