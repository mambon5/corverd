#!/bin/bash

# Directori del projecte Django
cd /var/www/corverd

# Enllaç d'exportació directa a TSV de la teva pestanya de Google Sheets
# (Recorda assegurar-te a Google Drive que l'accés estigui configurat com "Qualsevol persona amb l'enllaç pot veure")
GOOGLE_SHEET_URL="https://docs.google.com/spreadsheets/d/1urwR9jcDPO76JMGcm-dncu0oRfSO0MC4szckLOBpJFs/export?format=tsv&gid=1657285856"
FITXER_DESTI="fitxes_entitats_cv2.tsv"

echo "Descarregant l'últim fitxer TSV de Google Sheets..."
curl -L -s "$GOOGLE_SHEET_URL" -o "$FITXER_DESTI"

# Comprovem si s'ha descarregat correctament i no està buit
if [ -s "$FITXER_DESTI" ]; then
    echo "Fitxer descarregat correctament. Executant importació de Django..."
    /var/www/corverd/venv/bin/python3 manage.py importa_tsv_entitats "$FITXER_DESTI"
    echo "Importació finalitzada amb èxit."
else
    echo "ERROR: No s'ha pogut descarregar el fitxer TSV o està buit. Revisa l'enllaç o els permisos."
    exit 1
fi