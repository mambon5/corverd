# Coordinadora Verda - Migració a Django

Aquest projecte ha estat migrat d'una pàgina web estàtica a una aplicació operativa de Django amb integració d'una base de dades MySQL.

## Característiques Principals
- **Landing Page original:** Mantinguda a la vista principal (`/`).
- **Models de Base de Dades:** `Associacio`, `Activitat`, `Noticia`, i `Comentari`.
- **Rols d'Usuaris:** Panell d'administració on els administradors globals ho veuen tot i els "admins d'associació" només gestionen la seva pròpia entitat.
- **Vistes Públiques:**
  - `/entitats/`: Llista totes les entitats i mostren la seva informació bàsica, les darreres notícies i un mapa de localització mitjançant **Leaflet**.
  - `/noticia/<id>/`: Pàgina on s'ubica una notícia específica, i on els usuaris registrats poden comentar.

## 🚀 Com executar l'aplicació localment

Si ja tens l'entorn configurat, segueix aquests passos per aixecar el servidor de desenvolupament:

1. **Entra al directori del projecte**:
   ```bash
   cd /var/www/corverd
   ```

2. **Activa l'entorn virtual**:
   ```bash
   source venv/bin/activate
   ```

3. **Inicia el servidor de Django**:
   ```bash
   python manage.py runserver
   ```

> [!TIP]
> Si no es carreguen els estils o imatges localment, assegura't que el fitxer `.env` té `DEBUG=True`. Django no serveix fitxers estàtics automàticament si `DEBUG` és `False`.

L'aplicació estarà disponible a [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 🛠️ Guia d'Instal·lació Completa

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

### 4. Configurar la Base de Dades
El projecte utilitza MySQL. Necessites crear una base de dades i un usuari.
Pots fer-ho executant les següents comandes a la teva consola de MySQL (amb l'usuari root):

```sql
CREATE DATABASE coordinadoraverda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'corverd_user'@'localhost' IDENTIFIED BY 'la_teva_contrasenya';
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

- **Usuaris Representants (per a proves):**
  - Usuari: `representant_1` | Contrasenya: `password123` *(Associació de Defensa 1)*
  - Usuari: `representant_2` | Contrasenya: `password123` *(Associació de Defensa 2)*
  - Usuari: `representant_3` | Contrasenya: `password123` *(Associació de Defensa 3)*

*(Recorda canviar les contrasenyes o crear nous usuaris abans de passar a producció)*.

### 4. Gestió d'Entitats al Mapa (Leaflet)
Al tauler d'administració `/admin`, pots crear noves instàncies d'**Associació**. Segueix aquests passos per que apareguin al mapa de `/entitats/`:
1. Completa el camp **Latitud** i **Longitud** de l'Entitat (Exemple per Barcelona centre: Lat=41.3879, Lng=2.1699).
2. L'entitat apareixerà llavors llistada a `/entitats/` amb el seu pin corresponent al visor Leaflet.

---

## 📂 Estructura d'Arxius de l'Aplicació

Aquesta és l'estructura de directoris del projecte, per entendre quines carpetes conformen el **Front-end**, el **Back-end** i quines són residuals o duplicades:

### ⚙️ Back-end (Codi base i lògica)
- **`core/`**: És l'aplicació (app) principal de Django. Aquí s'hi troben els models de dades (`Associacio`, `Activitat`, `Noticia`, etc.), les vistes (lògica) i les rutes (urls) principals.
- **`serveis/`**: Sembla ser una aplicació secundària de Django destinada a gestionar alguna altra part específica del projecte (serveis).
- **`corverd_project/`**: És la carpeta de configuració global de Django. Inclou `settings.py` (configuracions, base de dades, directrius de seguretat) i `urls.py` (el router principal).
- **`manage.py`**: Arxiu del sistema, és l'entrada del projecte per executar comandes com arrencar el servidor, aplicar canvis a la base de dades o recollir fitxers estàtics.

### 🎨 Front-end (Interfície d'usuari)
- **`templates/`**: Conté tots els arxius `.html` (plantilles de Django). És la **base del Front-end**, les pantalles base on s'hi encasta la informació i on s'estructura el que veurà l'usuari.
- **`static/`**: Conté el disseny principal: imatges del disseny, el codi CSS pur i els arxius personals de JavaScript.

### 🌐 Carpetes servides al públic (En ús actiu)
- **`staticfiles/`**: Funciona com una **còpia duplicada (però necessària)** de tot el que hi ha a `static/`, sumant-hi recursos del propi sistema del panell d'admin. Aquesta és la carpeta que **s'està servint realment en producció** quan un usuari entra a la web. (Es genera amb la comanda de muntatge `collectstatic`).
- **`media/`**: Carpeta destinada als arxius dinàmics. Aquí és on s'emmagatzema qualsevol arxiu, foto o document que pugi un usuari i es serveix automàticament a la web (fotos de perfil, fotos de notícies...).

### 🗑️ Carpetes i Arxius No Utilitzats (Residuals)
> Tens tota la raó, hi ha elements que actualment no fan cap funció a l'app servida, la majoria producte del procés de migració, i que podrien ser esborrats si ja s'han utilitzat:
- **`coordinadoraverda.cat/`**: Aquesta carpeta conté un copiat / càpia sencera ("scrape") de l'antiga web (probablement la de WordPress, hi ha `.html` estàtics, i tot el codi de wp-content, wp-includes, etc.). **No s'està servint**, no té ús i pesa força.
- **Scripts de Python solts a l'arrel (`add_entrar_nav.py`, `fix_paths.py`, `replace_nav.py`, `seed.py`, etc.)**: Són scripts de procediment usats segurament durant la migració de l'antic format per arreglar l'HTML en massa o popular informació d'exemple a la base de dades. **No s'estan utilitzant per l'aplicació**.


# Per reiniciar la app heu d'executar:


```
git pull
sudo systemctl restart corverd
```