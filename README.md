# Coordinadora Verda - Migració a Django

Aquest projecte ha estat migrat d'una pàgina web estàtica a una aplicació operativa de Django amb integració d'una base de dades MySQL.

## Característiques Principals
- **Landing Page original:** Mantinguda a la vista principal (`/`).
- **Models de Base de Dades:** `Associacio`, `Activitat`, `Noticia`, i `Comentari`.
- **Rols d'Usuaris:** Panell d'administració on els administradors globals ho veuen tot i els "admins d'associació" només gestionen la seva pròpia entitat.
- **Vistes Públiques:**
  - `/entitats/`: Llista totes les entitats i mostren la seva informació bàsica, les darreres notícies i un mapa de localització mitjançant **Leaflet**.
  - `/noticia/<id>/`: Pàgina on s'ubica una notícia específica, i on els usuaris registrats poden comentar.

## Guia d'Instal·lació i Execució Local

### 1. Requisits
Tens preparades unes dependències a l'entorn virtual que has d'activar, i la base de dades `coordinadoraverda` ja està lligada i configurada.

### 2. Activació de l'Entorn Virtual i Execució

Per posar en marxa l'aplicació en un entorn local (des del directori `/var/www/corverd`):

```bash
# Activar l'entorn virtual
source venv/bin/activate

# Iniciar el servidor de desenvolupament
python manage.py runserver 0.0.0.0:8000
```
Després, només caldrà visitar `http://localhost:8000` des del navegador.

## Instal·lació en un nou servidor

Si vols instal·lar l'aplicació des de zero en un nou servidor Linux, segueix aquests passos:

### 1. Clonar el repositori i preparar l'entorn
```bash
git clone <url-del-repositori>
cd corverd
```

### 2. Crear i activar l'entorn virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal·lar les dependències
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar la Base de Dades MySQL
Crea una base de dades i un usuari a MySQL:
```sql
CREATE DATABASE coordinadoraverda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'corverd_user'@'localhost' IDENTIFIED BY 'coordi123';
GRANT ALL PRIVILEGES ON coordinadoraverda.* TO 'corverd_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar les dades de l'entorn (.env)
Copia el fitxer d'exemple i edita'l amb les teves dades:
```bash
cp .env.example .env
nano .env  # O el teu editor preferit
```
Assegura't que els paràmetres de la base de dades coincideixin amb els que has creat al pas anterior.

### 6. Aplicar migracions i crear superusuari
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Recollir fitxers estàtics (per a producció)
```bash
python manage.py collectstatic
```

### 3. Accés a l'Administració
L'aplicació compta amb un tauler d'administrador central per gestionar-ho tot.

- **URL:** `http://localhost:8000/admin/`
- **Superusuari per defecte:**
  - Usuari: `admin`
  - Contrasenya: `admin`

*(Recorda canviar la contrasenya o crear nous superusuaris abans de passar a producció)*.

### 4. Gestió d'Entitats al Mapa (Leaflet)
Al tauler d'administració `/admin`, pots crear noves instàncies d'**Associació**. Segueix aquests passos per que apareguin al mapa de `/entitats/`:
1. Completa el camp **Latitud** i **Longitud** de l'Entitat (Exemple per Barcelona centre: Lat=41.3879, Lng=2.1699).
2. L'entitat apareixerà llavors llistada a `/entitats/` amb el seu pin corresponent al visor Leaflet.
