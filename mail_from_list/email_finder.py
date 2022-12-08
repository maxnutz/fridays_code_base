# erstellen von e-mail-Verteilern: fasst die mails aus einer excel-liste zusammen
# Spalte mit E-Mail muss "E-Mail-Adresse" heißen, die Datei muss "Medien.csv" heißen.
# ausgabe: eine txt-Datei mit allen Adressen zusammen, getrennt durch Beistriche

import pandas as pd
df = pd.read_csv('Journaliste20220831.csv')
all_address = ''
for v in df['E-Mail-Adresse']:
	if not pd.isna(v):
		all_address += (v+', ')
with open('Journaliste20220831.txt', 'w') as text_file:
	text_file.write(all_address)
