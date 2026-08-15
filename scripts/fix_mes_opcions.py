import os
import re

directory = '/var/www/corverd/templates/'
for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as file:
                content = file.read()
            
            # replace href="something#"><span class="...">Més opcions
            new_content = re.sub(
                r'(<a\s+[^>]*?)href="[^"]*"\s*(>\s*<span[^>]*>Més opcions)', 
                r'\1href="#" onclick="return false;"\2', 
                content
            )
            
            if new_content != content:
                with open(filepath, 'w') as file:
                    file.write(new_content)
                print(f"Updated Més opcions link in {filepath}")
