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
smtp.login('noe@fridaysforfuture.at', 'Zt7xnkNq8RCUb8h3')

#Mailinhalt erstellen
subject = 'Weltweiter Klimastreik 25.3. in St. Pölten'
text = 'Wir wissen schon lange, dass die Klimakrise immer mehr drängt und die Politik nicht handelt. Die Klimakrise bekommen wir mittlerweile selbst in Österreich zu spüren durch Hochwasser, Hitzeperioden oder Starkregen und sie ist nicht mehr zu leugnen.\n\nDie Schule als Bildungseinrichtung hat die Aufgabe grundlegendes Wissen, Entscheidungsfähigkeit und Handlungskompetenz über die Klimakrise zu vermitteln.\n\nZiel der Schulbildung ist es auch, die Schülerinnen und Schüler zu befähigen, sich mit Wertvorstellungen und ethischen Fragen im Zusammenhang mit Natur und Technik sowie Mensch und Umwelt auseinander zu setzen. Eine Demonstration ist ein Werkzeug unserer demokratischen Mitbestimmung.\n\nWissen über und Verständnis für gesellschaftliche (insbesondere politische, wirtschaftliche, rechtliche, soziale, ökologische, kulturelle) Zusammenhänge ist eine wichtige Voraussetzung für ein bewusstes und eigenverantwortliches Leben und für eine konstruktive Mitarbeit an gesellschaftlichen Aufgaben.\n\nWir von Fridays for Future St. Pölten bitten Sie daher, sich als Schule hinter uns zu stellen und den Schüler:innen nichts in den Weg zu stellen, wenn sie sich für ihre Zukunft am 25.3. im Rahmen des 9. weltweiten Klimastreiks stark machen.\n\nAußerdem würden wir uns freuen, wenn wir vor dem Streik ein Plakat in der Schule aufhängen und in den kommenden Wochen vor dem Klimastreik vor der Schule Flyer an die Schüler:innen verteilen dürfen.\n\nNoch ist es möglich, das Schlimmste zu verhindern. Die nächsten Jahre sind die entscheidendsten und jede:r kann in dieser wichtigen Zeit Teil der Lösung sein!\n\nBitte denken Sie an die Zukunft der Ihnen anvertrauten Kinder und Jugendlichen und unterstützen Sie uns dabei! Bei Fragen können Sie uns gerne unter noe@fridaysforfuture.at bzw. 0699/11131745 erreichen. \n\nMit freundlichen Grüßen,\n\nVeronika von FFF Tulln\nJohanna und Flora von FFF St. Pölten\nMax von FFF Krems\nund Valentin von FFF Amstetten'

#Mailadressen und Anreden
data = pd.read_csv('/home/max/Dokumente/Privat/FFF_Krems/25.03/SchulenNOE.csv')
#print(data['Anrede'][1])
for v in tqdm(range(40, data.index.size)):

	smtp = smtplib.SMTP('w018feeb.kasserver.com')
	smtp.ehlo()
	smtp.starttls()
	smtp.login('noe@fridaysforfuture.at', 'Zt7xnkNq8RCUb8h3')


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

print('EOF with mail ', data['E-Mail-Adresse'][v])
