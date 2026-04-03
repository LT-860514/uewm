import os
import re
import time
from pathlib import Path
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='zh-CN', target='en')

def translate_chunk(chunk):
    if not chunk.strip(): return chunk
    try:
        res = translator.translate(chunk)
        return res
    except Exception as e:
        print(f"Error translating chunk, waiting 5s. Exception: {e}")
        time.sleep(5)
        try:
            return translator.translate(chunk)
        except:
            return chunk

def translate_file(src, dst):
    print(f"Translating {src} -> {dst}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()
        
    parts = content.split('\n\n')
    final_parts = []
    
    curr = []
    c_len = 0
    for p in parts:
        plen = len(p)
        if c_len + plen + 2 > 2000 and curr:
            chunk = '\n\n'.join(curr)
            if re.search(r'[\u4e00-\u9fff]', chunk):
                final_parts.append(translate_chunk(chunk))
            else:
                final_parts.append(chunk)
            curr = [p]
            c_len = plen
        else:
            curr.append(p)
            c_len += plen + 2
    if curr:
        chunk = '\n\n'.join(curr)
        if re.search(r'[\u4e00-\u9fff]', chunk):
            final_parts.append(translate_chunk(chunk))
        else:
            final_parts.append(chunk)

    final_content = '\n\n'.join(final_parts)
    
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    src_dir = Path(r"E:\projects\AI\uewm_master\docs\zh\design")
    dst_dir = Path(r"E:\projects\AI\uewm_master\docs\en\design")
    
    md_files = list(src_dir.rglob("*_V2.0.1.md"))
        
    total = len(md_files)
    print(f"Starting single-threaded batch translation for {total} files...")
    for i, md_file in enumerate(md_files):
        rel_path = md_file.relative_to(src_dir)
        target_file = dst_dir / rel_path
        sys_print = f"[{i+1}/{total}] "
        print(sys_print, end="")
        translate_file(str(md_file), str(target_file))
        
    print("Done.")
