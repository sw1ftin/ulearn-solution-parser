import requests
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
auth_token = os.getenv("ulearn.auth")

# ==========================================
# YOUR VALUES HERE
file_extension = "py"
course = "ml"
# ==========================================

if not os.path.exists("solutions"):
    os.mkdir("solutions")

url = f"https://ulearn.me/courses/{course}"
link = f"https://api.ulearn.me/courses/{course}"

response = requests.get(link)
data = json.loads(response.text)

title = data["title"]
id = data["id"]
units = data["units"]

if not os.path.exists(f"solutions/{id}"):
    os.mkdir(f"solutions/{id}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
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
    for unit in units:
        if not os.path.exists(f"solutions/{id}/{unit['title']}"):
            os.mkdir(f"solutions/{id}/{unit['title']}")
        slides = unit["slides"]
        for slide in slides:
            print(f'Parsing "{slide["title"]}"...')
            page.goto(f"https://ulearn.me/course/{course}/{slide['slug']}")
            page.wait_for_selector(".CodeMirror")
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
                f'Saved "{slide["title"]}.{file_extension}" in "solutions/{id}/{unit["title"]}/"\n\n'
            )
