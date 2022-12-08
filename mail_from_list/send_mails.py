
"""
Programm zum personalisierten Versenden von Mails
env: webprogramming
run with: python3 send_mail.py in respective folder
"""
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import pandas as pd
from tqdm import tqdm

smtp = smtplib.SMTP('w018feeb.kasserver.com')
smtp.ehlo()
smtp.starttls()
smtp.login('noe@fridaysforfuture.at', 'Whn1E!')

#Mailinhalt erstellen
subject = 'Weltweiter Klimastreik 25.3. in St. Pölten'
text = 'Am Freitag, den 23. September 2022 kommt der nächste weltweite Klimastreik - auch in St. Pölten wird eine Demonstration stattfinden, diesmal erst um 13:30 Uhr. \n\nDer Sommer zeigt, dass uns die Klimakrise nicht mehr nur bevorsteht, sondern längst angekommen ist - auch in Österreich. Überall in Europa brennen hektarweise Wälder nieder. Hitzetage und Tropennächte, Trockenheiten und Starkregenereignisse nehmen drastisch zu - „Was früher ein Rekord war, ist heute Durchschnitt“, heißt es von der ZAMG (Zentralanstalt für Meteorologie und Geodynamik). Wir brauchen umgehend umfassende Klimaschutzmaßnahmen, aber leider ist unsere Politik viel zu zögerlich. Ein Weg für uns Jugendliche, politisch Gehör zu finden, sind Klimastreiks. \n\nWir von Fridays for Future Niederösterreich bitten Sie daher, sich als Schule hinter uns zu stellen und den Schüler:innen nichts in den Weg zu legen, wenn sie sich für unser aller Zukunft am 23.9. im Rahmen des weltweiten Klimastreiks stark machen. Diesmal erfolgt der Beginn erst um 13:30 Uhr, um eine Teilnahme mit dem Unterricht kompatibler zu machen.\n\nAußerdem würden wir uns freuen, wenn wir vor dem Streik ein Plakat in der Schule aufhängen und vor der Schule Flyer an die Schüler:innen verteilen dürfen.\n\nDie Schule als Bildungseinrichtung hat unter anderem die Aufgabe, grundlegendes Wissen, Entscheidungsfähigkeit und Handlungskompetenz auch in Hinblick auf die Klimakrise zu vermitteln, die aus wissenschaftlicher Sicht eine der größten Herausforderungen der Menschheit ist. \n\nSchülerinnen und Schüler sollen befähigt werden, sich mit Wertvorstellungen und ethischen Fragen im Zusammenhang mit Natur und Technik sowie Mensch und Umwelt auseinanderzusetzen. Eine Demonstration ist ein Werkzeug unserer demokratischen Mitbestimmung. \n\nWissen über und Verständnis für gesellschaftliche (insbesondere politische, wirtschaftliche, rechtliche, soziale, ökologische, kulturelle) Zusammenhänge ist eine wichtige Voraussetzung für ein bewusstes und eigenverantwortliches Leben und für eine konstruktive Mitarbeit an gesellschaftlichen Aufgaben. \n\nDie Klimakrise macht vielen Menschen unserer Generation Angst und angesichts der Größe des Problems sind viele daran, den Mut zu verlieren. Noch ist es jedoch zufolge wissenschaftlicher Erkenntnisse möglich, das Schlimmste zu verhindern. Die nächsten Jahre werden entscheidend sein und jede:r kann in dieser wichtigen Zeit Teil der Lösung sein. Wir bitten Sie, als Direktor:in im Rahmen Ihrer Möglichkeiten dazu beizutragen. \n\nBitte denken Sie an die Zukunft der Ihnen anvertrauten Kinder und Jugendlichen und unterstützen Sie uns dabei!\n\nMit freundlichen Grüßen,\n\nVeronika von FFF Tulln\nJohanna und Flora von FFF St. Pölten\nMax von FFF Krems\nund Valentin von FFF Amstetten'

#Mailadressen und Anreden
data = pd.read_csv('/home/max/Dokumente/Skripts/fridays_code_base/mail_from_list/SchulenNOE.csv')
#print(data['Anrede'][1])
for v in range(0, data.index.size):
	try:

		smtp = smtplib.SMTP('w018feeb.kasserver.com')
		smtp.ehlo()
		smtp.starttls()
		smtp.login('noe@fridaysforfuture.at', 'Whn1E!')


		mailinhalt = data['Anrede'][v] + ' ' + data['Name'][v] + ',\n\n' + text
		#print(mailinhalt)
		to = data['E-Mail-Adresse'][v]
		print(to,  '\n\n')
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg.attach(MIMEText(mailinhalt))
		smtp.sendmail(from_addr='noe@fridaysforfuture.at', 
				to_addrs=to,
				msg=msg.as_string())
		smtp.quit()
	except Exception as e:
		print('Error with email ', data['E-Mail-Adresse'], '. Need again. ', e)
print('EOF with mail ', data['E-Mail-Adresse'][v])
