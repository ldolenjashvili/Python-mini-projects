import pandas as pd

# Countries we need
countries = ["GEO", "CAN", "ISR", "AUS"]

# Get Data into right shape
df = pd.read_json("https://covid.ourworldindata.org/data/owid-covid-data.json")

df = df[countries].transpose()[["data"]]
output = []
for country, row in df.iterrows():
  for dct in row["data"]:
    dct["Country"] = country
    output.append(dct)

df = pd.DataFrame(output)

fields = ["date", "Country", "new_cases", "new_cases_per_million", "new_deaths", "new_deaths_per_million", "people_fully_vaccinated_per_hundred"]
df['date'] =  pd.to_datetime(df['date'], format='%Y-%m-%d')
df = df[fields].set_index("date")

# Get last day's data
last_date = df.last_valid_index()

table_for_email = df.loc[last_date]
table_for_email.reset_index(drop=True, inplace=True)

table_for_email = table_for_email.transpose().reset_index()[1:].rename(
    columns={"index": "Category", 
             0: "Georgia", 
             1: "Canada", 
             2: "Israel", 
             3: "Australia"}
    )

df.reset_index(inplace=True)

georgia = df[df['Country'] == "GEO"]
canada = df[df['Country'] == "CAN"]
israel = df[df['Country'] == "ISR"]
australia = df[df['Country'] == "AUS"]

# Generate Plots
import matplotlib.pyplot as plt

fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, sharex=False, sharey=False, figsize=(15, 30))
plt.style.use("default")
ax1.set_title("Georgia", size=15)
ax1.plot(georgia["date"], georgia["new_cases_per_million"], color="blue", label="New Cases per Million")
ax1.plot(georgia["date"], georgia["new_deaths_per_million"], linestyle="dashed", label="New Deaths per Million")
ax1.legend(loc="upper left")

ax2.set_title("Canada", size=15)
ax2.plot(canada["date"], canada["new_cases_per_million"], color="crimson", label="New Cases per Million")
ax2.plot(canada["date"], canada["new_deaths_per_million"], linestyle="dashed", label="New Deaths per Million")
ax2.legend(loc="upper left")

ax3.set_title("Israel", size=15)
ax3.plot(israel["date"], israel["new_cases_per_million"], color="orange", label="New Cases per Million")
ax3.plot(israel["date"], israel["new_deaths_per_million"], linestyle="dashed", label="New Deaths per Million")
ax3.legend(loc="upper left")

ax4.set_title("Australia", size=15)
ax4.plot(australia["date"], australia["new_cases_per_million"], color="purple", label="New Cases per Million")
ax4.plot(australia["date"], australia["new_deaths_per_million"], linestyle="dashed", label="New Deaths per Million")
ax4.legend(loc="upper left")

plt.plot()

# Save plot as PNG
img_format = 'png'
plt.savefig("figure.png", format=img_format)

# Setup E-mail
from email.message import EmailMessage
from email.utils import make_msgid
from pretty_html_table import build_table
import smtplib
import imghdr

# Enter your AppPassword here
password = "senderAppPassword"

sender = "senderEmail@gmail.com"
receiver = "receiverEmail@gmail.com"
mail_server = "smtp.gmail.com"
port_number = 465

# Generate pretty table for E-mail
output_table = build_table(table_for_email, "blue_light")

newMessage = EmailMessage()
newMessage['Subject'] = f"Data for {last_date.date()}"
newMessage['From'] = sender
newMessage['To'] = receiver

newMessage.set_content('Hello, please check the new data.')

figure_id = make_msgid()
newMessage.add_alternative("""\
<html>
  <head></head>
  <body>
    <p>Hello, please check the new data.</p>
""" + output_table + """
    <img src="cid:{figure_id}" />
  </body>
</html>
""".format(figure_id=figure_id[1:-1]), subtype='html')

# Add Plot PNG inline in the message
with open("figure.png", 'rb') as img:
    newMessage.get_payload()[1].add_related(img.read(), 'image', 'png',
                                     cid=figure_id)

# Add Plot PNG as an attachment
with open('figure.png', 'rb') as f:
    image_data = f.read()
    image_type = imghdr.what(f.name)
    image_name = f.name

newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

# Send an E-mail
with smtplib.SMTP_SSL(mail_server, port_number) as smtp:
    smtp.login(sender, password)
    smtp.send_message(newMessage)

