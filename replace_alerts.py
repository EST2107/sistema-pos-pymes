import os
import re

js_dir = r'c:\Users\HP\proyecto ethan\sistema-pos-pymes\app\static\js'

for filename in os.listdir(js_dir):
    if not filename.endswith('.js'):
        continue
        
    filepath = os.path.join(js_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'alert(' not in content:
        continue
        
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if 'alert(' in line:
            is_success = False
            for j in range(max(0, i-4), i+1):
                if 'if (result.success)' in lines[j] or 'if (r.success)' in lines[j] or 'exitosa' in line or 'alert(r.message)' in line or 'alert(result.message)' in line:
                    # Could still be an error if it's in the else block.
                    # Actually, if it's exactly alert(r.message) right after if (r.success), it's success.
                    # If there's an 'else {' between the 'if' and the 'alert', it's an error.
                    pass
            
            # Better heuristic: 
            # If the line contains 'Error', 'Stock insuficiente', 'inválidos', it's error (true).
            # If the line is just alert(result.message) and we are inside the success block.
            
            # Let's do simple regex replacement and fix logic:
            
            # If the string inside alert starts with 'Error' or contains error keywords, or it's an else block
            # Actually, I'll just replace 'alert(' with 'showCustomAlert('
            # And I'll manually check for success later if needed. But wait, I can just do:
            # showCustomAlert(..., false) for specific success ones.
            
            # For simplicity, replace all `alert(x)` with `showCustomAlert(x)`
            line = re.sub(r'alert\((.*?)\)', r'showCustomAlert(\1)', line)
            
            # Now, fix the known success ones:
            # "Venta registrada exitosamente" was already removed.
            # alert(result.message) or alert(r.message) inside a success block.
            # Since my logic is simple, let's just do a blanket replace and I'll use multi_replace to fix the success ones.
            
        new_lines.append(line)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f'Updated {filename}')
