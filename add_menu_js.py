import os
import glob

html_files = glob.glob('/var/www/corverd/templates/**/*.html', recursive=True)

js_fix = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var openBtns = document.querySelectorAll('.wp-block-navigation__responsive-container-open');
    var closeBtns = document.querySelectorAll('.wp-block-navigation__responsive-container-close');
    var containers = document.querySelectorAll('.wp-block-navigation__responsive-container');

    openBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            containers.forEach(function(container) {
                container.classList.add('has-modal-open');
                container.classList.add('is-menu-open');
            });
        });
    });

    closeBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            containers.forEach(function(container) {
                container.classList.remove('has-modal-open');
                container.classList.remove('is-menu-open');
            });
        });
    });
});
</script>
</body>
"""

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "wp-block-navigation__responsive-container-open" in content and "<!-- WP_MENU_JS_FIX -->" not in content:
        # replace </body> with the script and </body>
        content = content.replace("</body>", "<!-- WP_MENU_JS_FIX -->" + js_fix)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
