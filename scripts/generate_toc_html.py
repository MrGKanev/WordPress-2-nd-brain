"""Generate a Table of Contents HTML from SUMMARY.md + print.html anchor IDs."""
import re
import sys


def extract_h1_ids(print_html_path):
    """Extract all h1 id→text mappings from print.html."""
    with open(print_html_path) as f:
        html = f.read()
    # Pattern: <h1 id="some-id"><a ...>Title Text</a></h1>
    matches = re.findall(r'<h1 id="([^"]+)"[^>]*><a[^>]*>(.+?)</a></h1>', html)
    # Build a lookup: normalized title → actual id
    lookup = {}
    for anchor_id, title in matches:
        key = normalize(title)
        lookup[key] = anchor_id
    return lookup


def normalize(text):
    """Normalize title for fuzzy matching."""
    text = re.sub(r'<[^>]+>', '', text)  # strip HTML tags
    text = text.lower().strip()
    text = text.replace('&amp;', ' ')    # HTML entity
    text = text.replace('&', ' ')        # raw ampersand
    text = re.sub(r'[^\w\s]', '', text)  # strip punctuation
    text = re.sub(r'\s+', ' ', text)
    return text


def parse_summary(summary_path):
    """Parse SUMMARY.md and return list of (indent_level, title)."""
    entries = []
    with open(summary_path) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            match = re.match(r'^(\s*)\*\s+\[(.+?)\]\((.+?)\)', line)
            if not match:
                continue
            indent = len(match.group(1)) // 2
            title = match.group(2)
            filepath = match.group(3)
            # Skip the root introduction; it is replaced by the generated TOC.
            if filepath == 'README.MD':
                continue
            entries.append((indent, title))
    return entries


def generate_html(entries, id_lookup):
    """Generate TOC HTML with proper links."""
    lines = []
    lines.append('<div class="pdf-toc">')
    lines.append('<h1 style="margin-top:1.5cm;margin-bottom:1cm;font-size:24pt">'
                 'Table of Contents</h1>')
    lines.append('<div style="font-family:Inter,sans-serif;font-size:10pt">')

    for indent, title in entries:
        key = normalize(title)
        anchor = id_lookup.get(key, '')
        href = f'href="#{anchor}"' if anchor else ''

        if indent == 0:
            lines.append(
                f'<div style="margin-top:0.8em;padding:4px 0;'
                f'font-weight:700;font-size:12pt;'
                f'border-bottom:1px solid #ddd">'
                f'<a {href} style="color:#000;text-decoration:none">'
                f'{title}</a></div>'
            )
        else:
            padding = indent * 18
            lines.append(
                f'<div style="padding:2px 0 2px {padding}px;'
                f'line-height:1.7;color:#333">'
                f'<a {href} style="color:#333;text-decoration:none">'
                f'{title}</a></div>'
            )

    lines.append('</div></div>')
    lines.append('<div style="break-before:page;page-break-before:always"></div>')
    return '\n'.join(lines)


if __name__ == '__main__':
    summary_path = sys.argv[1]
    print_html_path = sys.argv[2]
    output_path = sys.argv[3]

    id_lookup = extract_h1_ids(print_html_path)
    entries = parse_summary(summary_path)
    html = generate_html(entries, id_lookup)

    # Report unmatched entries
    for indent, title in entries:
        key = normalize(title)
        if key not in id_lookup:
            print(f'  WARNING: no anchor for "{title}"', file=sys.stderr)

    with open(output_path, 'w') as f:
        f.write(html)
