import os
import re

template_dir = 'templates'

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html') and file != 'nav.html':
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the start of the main navigation
            start_idx = content.find('<nav class="is-responsive items-justified-right wp-block-navigation')
            if start_idx != -1:
                # Find the matching closing </nav> tag
                # To be safe, we know the navigation ends before the language switcher or the WP_MENU_JS_FIX
                # Let's find the first </nav> after the start_idx
                end_idx = content.find('</nav>', start_idx)
                if end_idx != -1:
                    end_idx += len('</nav>')
                    
                    # We might have nested navs? Looking at the WP block, there are no nested navs.
                    # But just in case, let's verify if there are any <nav inside.
                    nav_content = content[start_idx:end_idx]
                    if '<nav' in nav_content[4:]:
                        print(f"Warning: Nested <nav> found in {filepath}. Manual intervention needed.")
                    else:
                        new_content = content[:start_idx] + "{% include 'nav.html' %}" + content[end_idx:]
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Replaced nav in {filepath}")
            else:
                print(f"No main nav found in {filepath}")
