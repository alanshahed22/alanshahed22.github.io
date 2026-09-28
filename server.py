#!/usr/bin/env python3
"""
Blog Publisher Server & Local App for Alan Shahed
Provides a distraction-free writing UI to author, preview,
and automatically publish posts directly to GitHub Pages.
"""

import os
import sys
import json
import re
import subprocess
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, 'posts')
INDEX_FILE = os.path.join(BASE_DIR, 'index.html')
PORT = 4321

def format_content_to_html(raw_text):
    """
    Converts plain text / markdown into clean semantic HTML.
    If the user already entered HTML tags, keeps them intact.
    """
    text = raw_text.strip()
    if not text:
        return "<p></p>"

    # Check if text already looks like full HTML blocks
    has_html_blocks = bool(re.search(r'<(p|h[1-6]|ul|ol|table|blockquote|div)[\s>]', text, re.IGNORECASE))
    if has_html_blocks:
        return text

    lines = text.split('\n')
    output_html = []
    in_code_block = False
    code_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Code block handling
        if stripped.startswith('```'):
            if in_code_block:
                code_content = '\n'.join(code_lines)
                output_html.append(f'<pre><code>{escape_html(code_content)}</code></pre>')
                code_lines = []
                in_code_block = False
            else:
                if in_list:
                    output_html.append('</ul>')
                    in_list = False
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Bullet list handling
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                output_html.append('<ul>')
                in_list = True
            item_text = format_inline(stripped[2:])
            output_html.append(f'  <li>{item_text}</li>')
            continue
        else:
            if in_list:
                output_html.append('</ul>')
                in_list = False

        # Blank line
        if not stripped:
            continue

        # Headings
        if stripped.startswith('### '):
            output_html.append(f'<h3>{format_inline(stripped[4:])}</h3>')
        elif stripped.startswith('## '):
            output_html.append(f'<h2>{format_inline(stripped[3:])}</h2>')
        elif stripped.startswith('# '):
            output_html.append(f'<h2>{format_inline(stripped[2:])}</h2>')
        # Blockquote
        elif stripped.startswith('> '):
            output_html.append(f'<blockquote><p>{format_inline(stripped[2:])}</p></blockquote>')
        # Regular paragraph
        else:
            output_html.append(f'<p>{format_inline(stripped)}</p>')

    if in_list:
        output_html.append('</ul>')
    if in_code_block and code_lines:
        code_content = '\n'.join(code_lines)
        output_html.append(f'<pre><code>{escape_html(code_content)}</code></pre>')

    return '\n    '.join(output_html)

def escape_html(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))

def format_inline(text):
    # Escape dangerous HTML first if plain text
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italics
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text

def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    if not slug:
        slug = f"post-{datetime.now().strftime('%Y%m%d%H%M')}"
    return f"{slug}.html"

def update_index_html(slug, title, date_str, formatted_date):
    if not os.path.exists(INDEX_FILE):
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_item = f'''      <li>
        <a href="posts/{slug}">{title}</a>
        <time datetime="{date_str}">{formatted_date}</time>
      </li>'''

    # If post already linked, replace it
    existing_pattern = re.compile(
        rf'<li>\s*<a href="posts/{re.escape(slug)}">.*?</a>\s*<time datetime=".*?">.*?</time>\s*</li>',
        re.DOTALL
    )
    if existing_pattern.search(content):
        content = existing_pattern.sub(new_item.strip(), content)
    else:
        # Insert at the top of <ul class="post-list">
        target = '<ul class="post-list">'
        if target in content:
            content = content.replace(target, f'{target}\n{new_item}', 1)
        else:
            # Fallback before </main>
            content = content.replace('</main>', f'{new_item}\n</main>', 1)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

class BlogHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/' or parsed.path == '/editor':
            editor_path = os.path.join(BASE_DIR, 'editor.html')
            if os.path.exists(editor_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(editor_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        elif parsed.path == '/api/posts':
            posts = []
            if os.path.exists(POSTS_DIR):
                for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
                    if filename.endswith('.html') and filename != 'template.html':
                        filepath = os.path.join(POSTS_DIR, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = f.read()
                            title_match = re.search(r'<h1>(.*?)</h1>', data)
                            time_match = re.search(r'<time datetime="(.*?)">(.*?)</time>', data)
                            title = title_match.group(1) if title_match else filename
                            date_str = time_match.group(1) if time_match else ''
                            date_display = time_match.group(2) if time_match else ''
                            posts.append({
                                'slug': filename,
                                'title': title,
                                'date': date_str,
                                'dateDisplay': date_display
                            })
                        except Exception:
                            continue

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(posts).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/publish':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode('utf-8'))
                title = data.get('title', '').strip()
                custom_slug = data.get('slug', '').strip()
                raw_content = data.get('content', '').strip()
                date_input = data.get('date', '').strip()

                if not title:
                    self.send_json_error(400, "Post title cannot be empty.")
                    return

                if not raw_content:
                    self.send_json_error(400, "Post content cannot be empty.")
                    return

                slug = slugify(custom_slug if custom_slug else title)

                # Format Date
                try:
                    dt = datetime.strptime(date_input, '%Y-%m-%d') if date_input else datetime.now()
                except ValueError:
                    dt = datetime.now()

                date_iso = dt.strftime('%Y-%m-%d')
                formatted_date = dt.strftime('%B %-d, %Y')

                # Format Content
                body_html = format_content_to_html(raw_content)

                # Post HTML
                post_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(title)} - Alan Shahed</title>
  <meta name="description" content="{escape_html(title)}">
  <link rel="stylesheet" href="../style.css">
</head>
<body>

  <header>
    <a href="../index.html">&larr; Back to all posts</a>
  </header>

  <article>
    <h1>{escape_html(title)}</h1>
    <p><time datetime="{date_iso}">{formatted_date}</time></p>

    {body_html}
  </article>

  <footer>
    <p><a href="../index.html">&larr; Back to all posts</a></p>
  </footer>

</body>
</html>
'''

                # 1. Save post file
                os.makedirs(POSTS_DIR, exist_ok=True)
                post_path = os.path.join(POSTS_DIR, slug)
                with open(post_path, 'w', encoding='utf-8') as f:
                    f.write(post_html)

                # 2. Update index.html
                update_index_html(slug, title, date_iso, formatted_date)

                # 3. Git commit & push
                commit_msg = f"Publish post: {title}"
                cmd = f'cd "{BASE_DIR}" && git add posts/"{slug}" index.html && git commit -m "{commit_msg}" && git push origin main'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    # Return error details if push failed
                    self.send_json_error(500, f"Git push failed:\n{result.stderr or result.stdout}")
                    return

                live_url = f"https://alanshahed22.github.io/posts/{slug}"
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'title': title,
                    'slug': slug,
                    'liveUrl': live_url,
                    'localFile': f'posts/{slug}'
                }).encode('utf-8'))

            except Exception as e:
                self.send_json_error(500, f"Internal error: {str(e)}")
            return

        self.send_response(404)
        self.end_headers()

    def send_json_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))

def run_server():
    server_address = ('127.0.0.1', PORT)
    try:
        httpd = HTTPServer(server_address, BlogHandler)
    except OSError:
        # If port 4321 in use, try next
        server_address = ('127.0.0.1', PORT + 1)
        httpd = HTTPServer(server_address, BlogHandler)

    active_port = server_address[1]
    url = f"http://127.0.0.1:{active_port}"
    print(f"======================================================")
    print(f"  ✍️  Alan's Minimal Blog Editor & Auto-Publisher     ")
    print(f"======================================================")
    print(f" Running at: {url}")
    print(f" Opening your browser...")
    print(f" Press Ctrl+C in this terminal to stop the editor.")
    print(f"------------------------------------------------------")

    # Open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down editor server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
