import re
import html

def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    
    # 1. Escape HTML special characters so they don't break Telegram HTML parsing
    # but keep already valid/escaped HTML tags if they are there, or just escape everything.
    # To be safe, we escape everything first.
    text = html.escape(text)
    
    # 2. Extract and temporarily hide code blocks
    code_blocks = []
    def save_code_block(match):
        code = match.group(1)
        code_blocks.append(code)
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"
        
    text = re.sub(r'```(?:[a-zA-Z0-9_-]+)?\n?(.*?)\n?```', save_code_block, text, flags=re.DOTALL)
    
    # 3. Extract and temporarily hide inline code
    inline_codes = []
    def save_inline_code(match):
        code = match.group(1)
        inline_codes.append(code)
        return f"___INLINE_CODE_{len(inline_codes)-1}___"
    
    text = re.sub(r'`(.*?)`', save_inline_code, text)

    # 4. Handle headers: e.g., ### title or ## title or # title
    text = re.sub(r'^#{1,6}\s+(.*?)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    
    # 5. Handle bold text: **text** or __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
    
    # 6. Handle italic text: *text* or _text_
    # Match single asterisks not followed/preceded by spaces (avoids matching bullets or standalone asterisks)
    text = re.sub(r'\*(?!\s)([^\*]+?)(?<!\s)\*', r'<i>\1</i>', text)
    # Match single underscores with boundary requirements to avoid snake_case issues
    text = re.sub(r'(?<=^|\s)_(?!\s)([^_]+?)(?<!\s)_(?=$|\s|[.,!?;:])', r'<i>\1</i>', text)
    
    # 7. Handle links: [text](url) -> <a href="url">text</a>
    # Note: since we did html.escape, the URL characters like & might be &amp;, which is correct for HTML links.
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # 8. Restore inline code
    for i, code in enumerate(inline_codes):
        text = text.replace(f"___INLINE_CODE_{i}___", f"<code>{code}</code>")
        
    # 9. Restore code blocks
    for i, code in enumerate(code_blocks):
        text = text.replace(f"___CODE_BLOCK_{i}___", f"<pre>{code}</pre>")
        
    return text

# Test cases
test_texts = [
    "This is **bold** and *italic* text.",
    "Bullet points:\n* Point 1\n* Point 2",
    "Nested **bold *italic* bold** string.",
    "Snake case variable `my_variable_name` and some text with under_score.",
    "A link: [Google](https://google.com?q=hello&lang=en)",
    "Code block:\n```python\ndef test():\n    return 1\n```",
    "Headers:\n# H1\n## H2\n### H3",
    "Unclosed *asterisk or _underscore in normal sentence.",
]

for t in test_texts:
    print("--- ORIGINAL ---")
    print(t)
    print("--- HTML ---")
    print(markdown_to_html(t))
    print()
