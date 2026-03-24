import os
import re
import time
from pathlib import Path
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='zh-CN', target='en')

def chunk_text(text, max_len=3000):
    chunks = []
    # Split by lines to maintain the block structure perfectly
    lines = text.split('\n')
    current_chunk = []
    current_len = 0
    
    for l in lines:
        l_len = len(l)
        if current_len + l_len + 1 > max_len and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [l]
            current_len = l_len
        else:
            current_chunk.append(l)
            current_len += l_len + 1
            
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
        
    return chunks

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
    if os.path.exists(dst):
        with open(dst, 'r', encoding='utf-8') as f:
            content = f.read()
        if not re.search(r'[\u4e00-\u9fff]', content):
            print(f"Skipping {src} -> Already English")
            return
            
    print(f"Translating {src} -> {dst}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Chunk everything into 3000 char blocks
    # We do not separate out code blocks because we want Google to translate the Chinese in them.
    # We just translate block by block, preserving \n structure.
    
    # We separate by ``` language lines so they don't get messed up if possible
    # Actually, simplest is split file by \n\n into rough blocks
    parts = content.split('\n\n')
    final_parts = []
    
    # Group parts into chunks of size ~2000
    big_chunks = []
    curr = []
    c_len = 0
    for p in parts:
        plen = len(p)
        if c_len + plen + 2 > 2000 and curr:
            big_chunks.append('\n\n'.join(curr))
            curr = [p]
            c_len = plen
        else:
            curr.append(p)
            c_len += plen + 2
    if curr:
        big_chunks.append('\n\n'.join(curr))
        
    for chunk in big_chunks:
        if re.search(r'[\u4e00-\u9fff]', chunk):
            final_parts.append(translate_chunk(chunk))
        else:
            final_parts.append(chunk)

    final_content = '\n\n'.join(final_parts)
    
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    src_dir = Path(r"E:\projects\AI\UEWM\docs\zh")
    dst_dir = Path(r"E:\projects\AI\UEWM\docs\en")
    
    md_files = list(src_dir.rglob("*.md"))
    req_file = next((f for f in md_files if 'Requirements_V6.1' in f.name), None)
    if req_file:
        md_files.remove(req_file)
        md_files.insert(0, req_file)
        
    total = len(md_files)
    print(f"Starting single-threaded batch translation for {total} files...")
    for i, md_file in enumerate(md_files):
        rel_path = md_file.relative_to(src_dir)
        target_file = dst_dir / rel_path
        sys_print = f"[{i+1}/{total}] "
        print(sys_print, end="")
        translate_file(str(md_file), str(target_file))
        
    print("Done.")
