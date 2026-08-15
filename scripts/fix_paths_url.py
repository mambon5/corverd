import os
import re

directory = '/var/www/corverd/templates/'
for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as file:
                content = file.read()
            
            # replace url('../wp-content or url('wp-content
            new_content = re.sub(
                r'''url\((['"]?)(?:\.\./)*wp-''', 
                r'''url(\1/wp-''', 
                content
            )
            
            if new_content != content:
                with open(filepath, 'w') as file:
                    file.write(new_content)
                print(f"Updated url() in {filepath}")
