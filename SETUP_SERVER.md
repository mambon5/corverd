Aquí tens tot en format Markdown (.md) llest per copiar i enganxar 👇

# 🚀 Deploy Django en producció (Gunicorn + Nginx + systemd)

Aquesta guia explica com desplegar una web Django en un servidor Linux amb domini públic.

---

# ⚙️ 1. Crear servei systemd (Gunicorn)

Crea el fitxer:

```bash
sudo nano /etc/systemd/system/corverd.service

Contingut:

[Unit]
Description=Corverd Django App
After=network.target

[Service]
User=romanov
Group=www-data
WorkingDirectory=/var/www/corverd
Environment="PATH=/var/www/corverd/venv/bin"
ExecStart=/var/www/corverd/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/corverd/corverd.sock \
    corverd.wsgi:application

[Install]
WantedBy=multi-user.target
▶️ Activar el servei
sudo systemctl daemon-reload
sudo systemctl start corverd
sudo systemctl enable corverd

Comprovar estat:

sudo systemctl status corverd

🌐 2. Configurar Nginx

Instal·lar Nginx:

sudo apt install nginx
Crear configuració del lloc
sudo nano /etc/nginx/sites-available/corverd

Contingut:

server {
    listen 80;
    server_name coordinadoraverda.cat www.coordinadoraverda.cat;

    location /static/ {
        root /var/www/corverd;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/corverd/corverd.sock;
    }
}
Activar el lloc
sudo ln -s /etc/nginx/sites-available/corverd /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
🔐 3. Configurar DNS del domini

A la configuració del teu domini (coordinadoraverda.cat), afegeix:

Registre A
@ → IP_DEL_SERVIDOR
Opcional
www → IP_DEL_SERVIDOR
🔒 4. Activar HTTPS (recomanat)

Instal·lar Certbot:

sudo apt install certbot python3-certbot-nginx

Configurar SSL:

sudo certbot --nginx -d coordinadoraverda.cat -d www.coordinadoraverda.cat
⚙️ 5. Configuració Django

A settings.py:

DEBUG = False

ALLOWED_HOSTS = [
    "coordinadoraverda.cat",
    "www.coordinadoraverda.cat"
]

STATIC_ROOT = "/var/www/corverd/static/"
📦 6. Recollir fitxers estàtics
source venv/bin/activate
python manage.py collectstatic
🚀 7. Flux del sistema
Internet → Nginx → Gunicorn → Django
🔄 8. Actualitzar la web

Cada cop que facis canvis:

git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart corverd
📊 9. Logs i depuració

Veure logs del servei:

journalctl -u corverd -f
⚡ Resum
systemd → manté l'app viva
Nginx → serveix el domini
Gunicorn → executa Django
Certbot → HTTPS
DNS → apunta al servidor