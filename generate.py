import os
from pathlib import Path
from PIL import Image
from datetime import datetime
import subprocess
import re  # Added for filename processing

ROOT_DIR = Path(__file__).parent.resolve()
WALLPAPER_DIR = ROOT_DIR / "wallpapers"
HTML_FILE = ROOT_DIR / "index.html"


def generate_previews():
    print("[+] Generating previews...")
    for folder in WALLPAPER_DIR.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.png"):
            preview_path = file.with_stem(file.stem + "-preview").with_suffix(".jpg")
            if not preview_path.exists():
                try:
                    with Image.open(file) as img:
                        preview = img.resize((480, int(480 * img.height / img.width)))
                        preview.save(preview_path, "JPEG", quality=85)
                        print(f"  - Created preview: {preview_path}")
                except Exception as e:
                    print(f"  ! Error processing {file}: {e}")


# New helper function to format wallpaper names
def format_wallpaper_name(filename):
    # Remove resolution (e.g., -3840x2160)
    name = re.sub(r"-\d{3,5}x\d{3,5}$", "", filename)
    # Replace hyphens and underscores with spaces
    name = name.replace("-", " ").replace("_", " ")
    # Convert to title case
    name = name.title()
    return name


def build_html():
    print(f"[+] Generating HTML file at {HTML_FILE}")
    with open(HTML_FILE, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n<title>Sekiryl's Wallpapers</title>\n")
        f.write(
            """
<style>
body {
    font-family: sans-serif;
    background: #231e1c;
    color: #e3d8c9;
    padding: 2em;
}
section {
    margin-bottom: 3em;
}
.wallpaper-item {
    margin-bottom: 2em;
}
.wallpaper-title {
    font-size: 1.2em;
    font-weight: bold;
    margin: 0.5em 0;
}
img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}
a.button {
    margin-right: 1em;
    background: #3a3530;
    padding: 0.5em 1em;
    border-radius: 4px;
    color: #e3d8c9;
    text-decoration: none;
    display: inline-block;
    margin-top: 0.5em;
}
h2 {
    text-transform: capitalize;
    border-bottom: 2px solid #3a3530;
    padding-bottom: 0.3em;
}
hr {
    border: 0;
    height: 1px;
    background: #3a3530;
    margin: 2em 0;
}
footer {
    margin-top: 4em;
    font-size: 0.9em;
    color: #aaa;
}
</style>
</head>
<body>
"""
        )
        f.write(
            f"<h1>Wallpapers by Sekiryl</h1>\n<p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
        )

        for folder in sorted(WALLPAPER_DIR.iterdir()):
            if not folder.is_dir():
                continue
            f.write(f"<section>\n<h2>{folder.name.replace('-', ' ')}</h2>\n")
            for file in sorted(folder.glob("*.png")):
                preview_file = file.with_stem(file.stem + "-preview").with_suffix(
                    ".jpg"
                )
                xcf_file = file.with_suffix(".xcf")

                rel_preview = preview_file.relative_to(ROOT_DIR)
                rel_png = file.relative_to(ROOT_DIR)
                rel_xcf = xcf_file.relative_to(ROOT_DIR)

                # Get formatted name from filename
                display_name = format_wallpaper_name(file.stem)

                f.write(f"<div class='wallpaper-item'>\n")
                f.write(f"<div class='wallpaper-title'>{display_name}</div>\n")
                f.write(f"<img src='{rel_preview}' alt='{display_name}'><br>\n")
                f.write(
                    f"<a class='button' href='{rel_png}' download>Download PNG</a>\n"
                )
                if xcf_file.exists():
                    f.write(
                        f"<a class='button' href='{rel_xcf}' download>Download XCF</a>\n"
                    )
                f.write("</div>\n")
            f.write("</section>\n")

        f.write(
            f"""
<footer>
<p>© {datetime.now().year} Sekiryl. All wallpapers are released under a <strong>Creative Commons Attribution-ShareAlike 4.0</strong> license.</p>
<p>Feel free to remix, recolor, and use them for your setup!</p>
</footer>
</body>
</html>
"""
        )


def git_push():
    print("[+] Committing and pushing to Git...")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Update wallpapers and index"],
            cwd=ROOT_DIR,
            check=True,
        )
        subprocess.run(["git", "push"], cwd=ROOT_DIR, check=True)
        print("[✓] Pushed to repository.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Git error: {e}")


def main():
    generate_previews()
    build_html()
    git_push()


if __name__ == "__main__":
    main()
