import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import datetime 
import pytz

#database connection
conn = psycopg2.connect(database="your database name",
                        host="your host name",
                        user="your user name",
                        password="your password used during installing postgres",
                        port="your port number for postgres connection")
#read csv dataset
data=pd.read_csv('usa_county_wise.csv')
rows=data.shape[0]

cur=conn.cursor()
# inserting csv data to postgres database
cur.execute('create table usa_death(id SERIAL PRIMARY KEY,province_state varchar(20),country_region varchar(10),lat float,lon float,date_ date,confirmed int,deaths  int);')
 for i in range(0,rows):
    cur.execute('insert into usa_death values(%s,%s,%s,%s,%s,%s,%s,%s)',(i,data['Province_State'][i],data['Country_Region'][i],data['LAT'][i],data['LON'][i],data['Date'][i],int(data['Confirmed'][i]),int(data['Deaths'][i])))
conn.commit()


#getting the values for plotting from database
cur.execute('select sum(deaths) as total_deaths,sum(confirmed) as Total_confirmed_deaths from usa_death')
cur.execute('select deaths from usa_death')
deaths=cur.fetchall()
cur.execute('select confirmed from usa_death')
confirmed=cur.fetchall()
cur.execute('select date_ from usa_death')
date=cur.fetchall()

# plotting the histogram
plt.hist(deaths,bins='auto')
plt.hist(confirmed,bins='auto')

# saving the generated figure plt.savefig should be used before plt.show otherwise the saved figure will be blank
plt.savefig("fig.png")
plt.show(block=True)

# getting zone wise time for the mailing detail
today = datetime.date.today()
BDTz = pytz.timezone("Asia/Dhaka") 
timeInBD = datetime.datetime.now(BDTz)
currentTimeInBD = timeInBD.strftime("%H:%M:%S")

# connection establishment gor mail
sender_address = 'your email'
sender_pass = 'your password'
receiver_address = 'receiver email'
bcc='bcc email'
subject = "Histogram Report " + str(today)

#mail body
message = '''Dear sir,
Please Check the attached file.


Regards,
MD. Amir Abdal Sobhani
Software Engineer,
xyz company '''+ currentTimeInBD
msg = MIMEMultipart()
msg['From'] = sender_address
msg['To'] = receiver_address
msg['Bcc']=bcc
msg['Subject'] = subject

# attaching the body and figure in the mail
msg.attach(MIMEText(message, 'plain'))
#Setup the MIME
with open('fig.png', 'rb') as file:
    image = MIMEImage(file.read(), name='fig.png')
    msg.attach(image)
# Connect to the SMTP server and send the email
with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
    server.starttls()
    server.login(sender_address, sender_pass)
    server.send_message(msg)



