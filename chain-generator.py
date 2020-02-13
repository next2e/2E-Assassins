from configparser import ConfigParser
from csv import reader
from email.mime.text import MIMEText
from random import shuffle
from smtplib import SMTP_SSL
from time import sleep

# The csv should have the first column be Kerberoi. The second column should be their names. Other columns can be used for additional data.
with open('people.csv') as f:
    people = []
    r = reader(f)
    for line in r:
        people.append(line)
    print('Read {} people.'.format(len(people)))
    approved = False

    while not approved:
        print("Chain not yet generated or not approved. Generating chain.")
        # Perform shuffle of the chain.
        shuffle(people)
        print("This is what the chain looks like:")
        print(list(map(lambda person: person[1],people)))
        approved = True if input("Do you approve of this chain? [Y/n]: ") == "Y" else False

    # Read the credentials needed to send out emails.
    c = ConfigParser()
    c.read('config.ini')
    smtp = SMTP_SSL('outgoing.mit.edu')
    smtp.login(c['Credentials']['Kerberos'], c['Credentials']['Password'])

    for index, (kerberos, name, *_) in enumerate(people):
        # On all iterations but the last, the next person in the list is the target.
        if index + 1 < len(people):
            target = people[index + 1]
        # On the last iteration, the first person in the list is the target.
        else:
            target = people[0]
        msg = MIMEText(c['Message']['Template'].format(target[1], target[0], *target[2:]), 'html')
        msg['Subject'] = c['Message']['Subject']
        msg['From'] = c['From']['Display']
        msg['To'] = '{}@mit.edu'.format(kerberos)
        smtp.sendmail(c['From']['Email'], '{}@mit.edu'.format(kerberos), msg.as_string())
        print('Sent email to {} ({}) with target {} ({}). Waiting 5 seconds to cool down...'.format(name, kerberos, target[1], target[0]))
        sleep(5)
    smtp.close()
    print('Chain generated successfully!')
