import os
import re

directory = '/var/www/corverd/templates/'

new_links = """
{% if user.is_authenticated %}
<li class=" wp-block-navigation-item wp-block-navigation-link"><a class="wp-block-navigation-item__content"  href="{% url 'intranet_dashboard' %}"><span class="wp-block-navigation-item__label">Intranet</span></a></li>
<li class=" wp-block-navigation-item wp-block-navigation-link"><a class="wp-block-navigation-item__content"  href="{% url 'logout' %}"><span class="wp-block-navigation-item__label">Sortir</span></a></li>
{% else %}
<li class=" wp-block-navigation-item wp-block-navigation-link"><a class="wp-block-navigation-item__content"  href="{% url 'login' %}"><span class="wp-block-navigation-item__label">Entrar</span></a></li>
{% endif %}
"""

for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html') and filename != 'login.html':
            filepath = os.path.join(root, filename)
            with open(filepath, 'r') as file:
                content = file.read()
            
            if "{% url 'login' %}" not in content:
                # Target the 'Contacte' li block and insert right after it
                new_content = re.sub(
                    r'(<li[^>]*>\s*<a[^>]*href="\{%\s*url\s*\'contacte\'\s*%\}"[^>]*>\s*<span[^>]*>Contacte</span>\s*</a>\s*</li>)',
                    r'\1' + new_links,
                    content,
                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
                )
                
                if new_content != content:
                    with open(filepath, 'w') as file:
                        file.write(new_content)
                    print(f"Updated nav in {filepath}")
                else:
                    print(f"Skipping {filepath} (pattern not found)")
