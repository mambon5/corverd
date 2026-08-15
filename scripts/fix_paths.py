import os
import re

directory = '/var/www/corverd/templates/'
for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as file:
                content = file.read()
            
            # replace href="wp-content, src="wp-content, srcset="wp-content
            # also handles single quotes and ../
            new_content = re.sub(
                r'''(href|src|srcset)=(['"])(?:\.\./)*wp-''', 
                r'''\1=\2/wp-''', 
                content
            )
            
            if new_content != content:
                with open(filepath, 'w') as file:
                    file.write(new_content)
                print(f"Updated {filepath}")
