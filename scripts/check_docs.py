"""Documentation and Markdown link/asset integrity checker for SentinelEdge."""
import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md_files = []
for root, dirs, files in os.walk(base_dir):
    if any(x in root for x in [".git", "node_modules", ".pytest_cache"]):
        continue
    for f in files:
        if f.endswith(".md"):
            md_files.append(os.path.join(root, f))

print(f"Checking {len(md_files)} markdown files...")

link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
img_pattern = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']")

errors = 0
for mf in md_files:
    rel = os.path.relpath(mf, base_dir)
    with open(mf, "r", encoding="utf-8") as f:
        content = f.read()

    # Check backtick count
    code_fences = content.count("```")
    if code_fences % 2 != 0:
        print(f"[ERROR] Uneven code fences ({code_fences}) in {rel}")
        errors += 1

    # Check local links
    for text, url in link_pattern.findall(content):
        if url.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean_url = url.split("#")[0]
        if not clean_url:
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(mf), clean_url))
        if not os.path.exists(target):
            print(f"[BROKEN LINK] in {rel}: '{url}' -> not found at {target}")
            errors += 1

    # Check img tags
    for src in img_pattern.findall(content):
        if src.startswith(("http://", "https://", "data:")):
            continue
        clean_src = src.split("#")[0]
        target = os.path.normpath(os.path.join(os.path.dirname(mf), clean_src))
        if not os.path.exists(target):
            print(f"[BROKEN IMG] in {rel}: '{src}' -> not found at {target}")
            errors += 1

    # If file has TOC, check anchors
    if "Table of Contents" in content:
        headings = re.findall(r"^(#+)\s+(.+)$", content, re.MULTILINE)
        heading_slugs = set()
        for level, h in headings:
            slug = h.strip().lower()
            slug = re.sub(r"[^\w\s\-]", "", slug)
            slug = re.sub(r"[\s]+", "-", slug).strip("-")
            heading_slugs.add(slug)

        toc_anchors = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", content)
        for title, anchor in toc_anchors:
            if anchor not in heading_slugs:
                print(f"[BROKEN ANCHOR] in {rel}: [{title}](#{anchor})")
                errors += 1

print(f"Documentation check complete. Found {errors} issues.")
if errors > 0:
    exit(1)
