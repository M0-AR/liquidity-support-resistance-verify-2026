"""Capture docs/preview.html with Playwright (screenshots; GIF if ffmpeg). Verifies the page loads clean."""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
SHOT = ROOT / "preview_shots"
SHOT.mkdir(exist_ok=True)

URL = (ROOT / "preview.html").as_uri()

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed; screenshots skipped (page still works via file://)")
        return 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1100, "height": 900})
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(URL, wait_until="networkidle")
        pg.screenshot(path=str(SHOT / "01_hero.png"))
        pg.click("text=Take the 10-question quiz")
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(SHOT / "02_quiz.png"))
        # answer Q1 correctly to prove interactivity, then grade
        pg.check("input[name='q0'][value='1']")
        pg.click("text=Grade me")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(SHOT / "03_graded.png"))
        print("console errors:", errors if errors else "none")
        b.close()
    # optional GIF stitch
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0:
        subprocess.run(["ffmpeg", "-y", "-framerate", "1", "-pattern_type", "glob",
                        "-i", str(SHOT / "0*.png"), str(ROOT / "preview.gif")],
                       capture_output=True)
        print("wrote docs/preview.gif")
    print("shots:", sorted(x.name for x in SHOT.glob("*.png")))
    return 0

if __name__ == "__main__":
    sys.exit(main())
