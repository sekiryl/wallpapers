import os
from pathlib import Path
from PIL import Image
from datetime import datetime
import subprocess
import re
import argparse  # Added for argument parsing

ROOT_DIR = Path(__file__).parent.resolve()
WALLPAPER_DIR = ROOT_DIR / "wallpapers"
HTML_FILE = ROOT_DIR / "index.html"


def generate_previews(force=False):
    print("[+] Generating previews...")
    for folder in WALLPAPER_DIR.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.png"):
            preview_path = file.with_stem(file.stem + "-preview").with_suffix(".jpg")

            # Check if regeneration is needed
            regenerate = False
            if force:
                regenerate = True
                reason = "--force flag used"
            elif not preview_path.exists():
                regenerate = True
                reason = "preview missing"
            else:
                # Check modification times
                file_mtime = file.stat().st_mtime
                preview_mtime = preview_path.stat().st_mtime
                if file_mtime > preview_mtime:
                    regenerate = True
                    reason = "source file modified"

            if regenerate:
                try:
                    with Image.open(file) as img:
                        preview = img.resize((720, int(720 * img.height / img.width)))
                        preview.convert("RGB").save(preview_path, "JPEG", quality=85)
                        print(f"  - Regenerated preview ({reason}): {preview_path}")
                except Exception as e:
                    print(f"  ! Error processing {file}: {e}")
            else:
                print(f"  ✓ Preview up-to-date: {preview_path}")


def format_wallpaper_name(filename):
    name = re.sub(r"-\d{3,5}x\d{3,5}$", "", filename)
    name = name.replace("-", " ").replace("_", " ")
    return name.title()


def build_html():
    print(f"[+] Generating HTML file at {HTML_FILE}")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year

    with open(HTML_FILE, "w") as f:
        # HTML Head Section
        f.write(
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sekiryl's Wallpapers</title>
    
    <!-- Favicon -->
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon/favicon-16x16.png">
    <link rel="manifest" href="/assets/favicon/site.webmanifest">
    <link rel="shortcut icon" href="/assets/favicon/favicon.ico">
    <meta name="theme-color" content="#d4875d">
    <meta name="description" content="Download high-quality, original wallpapers by Sekiryl. Includes PNG and XCF files for customization." />
    <meta name="keywords" content="Sekiryl, wallpapers, original art, XCF wallpapers, PNG wallpapers, digital art, design" />
    <meta name="author" content="Sekiryl" />
    <link rel="canonical" href="https://walls.sekiryl.is-a.dev" />

    <meta property="og:title" content="Sekiryl's Wallpapers" />
    <meta property="og:description" content="A collection of original wallpapers designed by Sekiryl. Free to download in high resolution." />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://walls.sekiryl.is-a.dev" />
    <meta property="og:image" content="https://walls.sekiryl.is-a.dev/assets/images/logo.png" />

    <script type="application/ld+json">
    {{
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "name": "Sekiryl's Wallpapers",
    "url": "https://sekiryl.is-a.dev",
    "creator": {{
      "@type": "Person",
      "name": "Sekiryl",
      "url": "https://sekiryl.is-a.dev"
    }},
    "description": "A collection of high-resolution wallpapers created by Sekiryl, available in PNG and editable XCF formats.",
    "image": "https://walls.sekiryl.is-a.dev/assets/images/logo.png"
    }}
    </script>
    
    <style>
        :root {{
            --base: #231e1c;
            --mantle: #1a1614;
            --crust: #0f0d0c;
            --text: #e3d8c9;
            --subtext1: #c5b7a3;
            --subtext0: #a09585;
            --overlay2: #7a6e64;
            --overlay1: #5a5149;
            --overlay0: #3a3530;
            --surface2: #402f28;
            --surface1: #352c26;
            --surface0: #2a231e;
            --peach: #d4875d;
            --lavender: #7a6a9a;
            --blue: #3a5a7a;
            --teal: #4a8a8a;
            --pink: #b26888;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--mantle) 0%, var(--base) 100%);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem 1rem;
            background-attachment: fixed;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--surface0);
        }}
        
        .logo {{
            height: 80px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        .header-content {{
            flex: 1;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(45deg, var(--peach), var(--lavender));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .last-updated {{
            color: var(--subtext1);
            font-size: 1rem;
            display: block;
            margin-top: 0.25rem;
        }}
        
        .intro {{
            background: var(--surface0);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 3rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            border: 1px solid var(--overlay0);
        }}
        
        .intro p {{
            margin-bottom: 1rem;
            font-size: 1.05rem;
        }}
        
        .license {{
            display: inline-block;
            background: var(--surface1);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            border: 1px solid var(--overlay1);
        }}
        
        h2 {{
            font-size: 1.8rem;
            margin: 2.5rem 0 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--peach);
            color: var(--subtext1);
            text-transform: capitalize;
            position: relative;
        }}
        
        h2::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 80px;
            height: 2px;
            background: var(--lavender);
        }}
        
        .wallpaper-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}
        
        .wallpaper-item {{
            background: var(--surface0);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid var(--overlay0);
        }}
        
        .wallpaper-item:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            border-color: var(--overlay1);
        }}
        
        .wallpaper-preview {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
            transition: transform 0.4s ease;
        }}
        
        .wallpaper-item:hover .wallpaper-preview {{
            transform: scale(1.03);
        }}
        
        .wallpaper-content {{
            padding: 1.2rem;
        }}
        
        .wallpaper-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: var(--subtext1);
        }}
        
        .button-group {{
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
        }}
        
        .button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
            font-size: 0.95rem;
            border: 1px solid transparent;
        }}
        
        .button:hover {{
            transform: translateY(-2px);
        }}
        
        .button-png {{
            background: var(--surface1);
            color: var(--text);
            border-color: var(--overlay1);
        }}
        
        .button-png:hover {{
            background: var(--blue);
            border-color: var(--blue);
        }}
        
        .button-xcf {{
            background: var(--surface1);
            color: var(--text);
            border-color: var(--overlay1);
        }}
        
        .button-xcf:hover {{
            background: var(--teal);
            border-color: var(--teal);
        }}
        
        footer {{
            text-align: center;
            padding: 2.5rem 1rem 1rem;
            color: var(--subtext0);
            font-size: 0.95rem;
            margin-top: 2rem;
            border-top: 1px solid var(--surface0);
        }}
        
        @media (max-width: 768px) {{
            header {{
                flex-direction: column;
                text-align: center;
            }}
            
            .wallpaper-grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <img src="assets/images/logo.png" alt="Logo" class="logo">
            <div class="header-content">
                <h1>Sekiryl's Wallpapers</h1>
                <span class="last-updated">Last updated: {last_updated}</span>
            </div>
        </header>
        
        <div class="intro">
            <p>Welcome to my wallpaper collection! All artworks are created by me and available for you to use in your personal setups.</p>
            <p>Feel free to download, modify, and share these wallpapers according to the license terms.</p>
            <span class="license">Creative Commons Attribution-ShareAlike 4.0</span>
        </div>
"""
        )

        # Wallpaper Sections
        for folder in sorted(WALLPAPER_DIR.iterdir()):
            if not folder.is_dir():
                continue

            category_name = folder.name.replace("-", " ")
            f.write(f"<h2>{category_name}</h2>\n")
            f.write("<div class='wallpaper-grid'>\n")

            for file in sorted(folder.glob("*.png")):
                preview_file = file.with_stem(file.stem + "-preview").with_suffix(
                    ".jpg"
                )
                xcf_file = file.with_suffix(".xcf")

                rel_preview = preview_file.relative_to(ROOT_DIR)
                rel_png = file.relative_to(ROOT_DIR)
                rel_xcf = xcf_file.relative_to(ROOT_DIR)

                display_name = format_wallpaper_name(file.stem)

                f.write("<div class='wallpaper-item'>\n")
                f.write(
                    f"<img src='{rel_preview}' alt='{display_name}' class='wallpaper-preview'>\n"
                )
                f.write("<div class='wallpaper-content'>\n")
                f.write(f"<div class='wallpaper-title'>{display_name}</div>\n")
                f.write("<div class='button-group'>\n")
                f.write(
                    f"<a class='button button-png' href='{rel_png}' download>PNG</a>\n"
                )
                if xcf_file.exists():
                    f.write(
                        f"<a class='button button-xcf' href='{rel_xcf}' download>XCF</a>\n"
                    )
                f.write("</div>\n")  # .button-group
                f.write("</div>\n")  # .wallpaper-content
                f.write("</div>\n")  # .wallpaper-item

            f.write("</div>\n")  # .wallpaper-grid

        # Footer
        f.write(
            f"""
        <footer>
            <p>© {current_year} Sekiryl. All wallpapers are released under a <strong>Creative Commons Attribution-ShareAlike 4.0</strong> license.</p>
            <p>Feel free to remix, recolor, and use them for your setup!</p>
        </footer>
    </div>
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
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Generate wallpaper previews and index.html"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force regenerate all preview images"
    )
    args = parser.parse_args()

    generate_previews(force=args.force)
    build_html()
    git_push()


if __name__ == "__main__":
    main()
