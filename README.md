<h1>Quickbooks Online Connector for BTCPay Server</h1>

Copyright (C) 2018 Jeff Vandrew Jr

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
 
<h2>Introduction</h2>
 
Quickbooks Online (QBO) is currently the most popular small business bookkeeping solution, and is often used as an online invoicing solution. When customers receive an online invoice from a business using QBO, they currently have the option to pay electronically using credit card or ACH (via integrated Intuit Payments) or Bitcoin (via Intuit PayByCoin, which unfortunately only supports BitPay and Coinbase). This software extends Quickbooks Online to take payments through BTCPay server.

Customers choosing to pay a QBO invoice using BTCPay automatically have a BTCPay invoice generated with the customer's data pre-filled, and payments to the BTCPay invoice are autmatically recorded in QBO. Before generating the invoice, the software verifies that the email and invoice number match to prevent against customer typos.

<h2>Improvements Roadmap</h2>

1. Quicker install method. Since the BTCPay one-click install method deploys on an Ubuntu VPS, it seems the best way to accomplish this short-term is by creating a .deb.

2. I've included a rudimentary a CLI tool for manually refreshing QBO Oauth2 tokens. (The tokens auto-refresh without ever toughing the CLI; the CLI tool is simply for testing the connection to QBO.) Additional CLI functionality could be useful for activating/deactivating public access (currently accomplished via environmental variables) and other QBO connection testing purposes.

<h2>Notes</h2>

All payments made through BTCPay will be recorded in QBO in an "Other Current Asset" account called "Bitcoin." They are recorded at USD value as of the date the invoice was paid. This is not a bug; it is intentional behavior. The USD value on the payment date is the amount of taxable income recognized as well as the tax basis for a future sale of BTC under US Tax law, so the BTC is recorded in QBO accordingly. The information herein is educational only and is not tax advice; consult your tax professional.

<h2>Installation</h2>

Below are installation instructions for deployment on a LunaNode VPS that was set up via the one-click install recommended by the BTCPay team. More technical users can adapt these instructions for other setups.

<h3>Part 1: Obtain Intuit Keys</h3>

1. Head to https://developer.intuit.com and log in using the same login you normally use for Quickbooks Online. Your account will then be granted developer privileges.

2. After logging in, clock on "My Apps" and create a new app. The title is irrelevant.

3. After the "app" is created, click "Keys". There will be sandbox and production keys. To obtain the production keys, Intuit will require you to fully fill out your developer profile. Intuit will also require links to your privacy policy and EULA; these are largely irrelevant since your own business will the only "user" of your app. If you don't have links to a EULA and privacy policy, you may choose to use these links https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/privacy-sample and https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/eula-sample. This is not legal advice, and consult with your own attorney if you have questions. 

4. Underneath your Intuit keys, add "https://btcpay.example.com/btcqbo/qbologged" as a redirect URI, replacing btcpay.example.com with the domain where your BTCPay instance is hosted.

<h3>Part 2: Install BTCQBO</h3>

1. Log into your LunaNode VPS using SSH. 

2. Install redis-server, python3, python3-venv, and python3-dev. Assuming you've accessed LunaNode's Ubuntu VPS via SSH, this would done from the command line as follows:
`$ sudo apt-get install redis-server python3 python3-venv python3-dev`

2. Using systemd, enable redis-server.service, then start redis-server.service:
```
$ sudo systemctl enable redis-server.service
$ sudo systemctl start redis-server.service
```

3. Using git, clone this repository to a local directory:
`$ git clone https://github.com/JeffVandrewJr/btcqbo`

4. Change directory into the new 'btcqbo' directory, create a python venv and activate it:
```
$ python3 -m venv venv
$ source venv/bin/activate
```

5. Install dependencies by running:
`$ sudo pip install -r requirements.txt`

6. Create an .env file by running `$ cp env.sample .env` in the btcqbo directory. Then, using the text editor of your choice, open the .env (example using nano as a text editor: `$ nano .env`). Be sure to enter your "client ID" and "client secret" from the keys tab on the Intuit Developer site. Also change the callback URL to the URL you chose in the last step of Part 1. Finally, change the BTCPay server URL to the URL of your BTCPay instance. After you're done, save the .env file and exit.

7. Create, enable, and start the systemd unit files for btcqbo.service and rq-worker.service. To do so, from the btcqbo directory:
```
$ sudo cp btcqbo.service /etc/systemd/system/btcqbo.service
$ sudo cp rq-worker.service /etc/systemd/system/rq-worker.service
$ sudo enable btcqbo.service
$ sudo enable rq-worker-service
$ sudo start btcqbo.service
$ sudo start rq-worker.service
```

8. Make a copy of the nginx default.conf out of its Docker container: `sudo docker cp nginx:/etc/nginx/conf.d/default.conf .`. Don't forget the trailing period.

9. Open the default.conf you just copied in the text editor of your choice (example: `nano default.conf`) Just before the final closing curly brace in the file, add this code:
```
location /btcqbo/ {
proxy_pass http://XXX.XX.XXX.XX:8001;
proxy_redirect off;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
The X's above need to be replaced with your an IP address that your container resolves to localhost. To find this, run:
`sudo docker network inspect generated_default`. Under "Config", there will be an entry for "Gateway". That will be the IP address to use. Don't forget to append the :8001 to the end as shown above. When you save the file, you may need to override its read-only status. In vim this is accomplished via `:w!`; other text editors should prompt you on screen for the override if necessary.

9. Copy the default.conf file back into the nginx Docker container: `sudo docker cp default.conf nginx:/etc/nginx/conf.d/default.conf`

10. Restart nginx (the final exit is critical to avoid corrupting your nginx container):
```
$ sudo docker exec -it nginx /bin/bash
# service nginx reload
# exit
```
<h3>Part 3: Sync with Intuit & BTCPay</h3>

1. From a web browser, visit https://btcpay.example.com/btcqbo/authqbo, replacing btcqbo.example.com with your domain.

2. Follow the steps to sync to Inuit.

3. Go log into your BTCPay server, click on your store, and then hit settings. From the settings menu, create an authorization token. Once the token is created, BTCPay will provide a pairing code.

4. From a web browser, visit https://btcpay.example.com/btcqbo/authbtc, replacing btcqbo.example.com with your domain. Enter the pairing code from the step above, and submit.

5. Disable public access by editing your .env file to change AUTH_ACCESS to `False` (capital 'F'). Then restart btcqbo.service for the change to take effect (`$ sudo systemctl restart btcqbo`).

<h3>Part 4: The Public Facing Payment Portal</h3>

These instructions assume your business' public facing page is a Wordpress site. 

1. Create a new page on your Wordpress site. Title it "Make a Bitcoin Payment". Set the URL so to something short, like example.com/pay.

2. Paste the code below into the body:
```
<form method="POST" action="https://btcpay.example.com/btcqbo/verify">
USD Amount:
  <input type="text" name="amount" />
Email Address:
  <input type="text" name="email" />
Invoice Number:
  <input type="text" name="orderId" />
  <input type="hidden" name="notificationUrl" value="https://btcpay.example.com/btcqbo/api/v1/payment" />
  <input type="hidden" name="redirectUrl" value="https://example.com" />
  <button type="submit">Pay now</button>
</form>
```

4. In the code, change btcpay.example.com to your appropriate domain, and set the redirect URL of your choice. Save the page in Wordpress; due to the magic of CSS it should automatically be styled to match your site.

5. In Quickbooks Online, edit your outgoing email template for invoicing with a concluding paragraph like this one:

`"Click "Review and Pay below to pay via ACH or Credit Card, or click https://example.com/pay to bay via Bitcoin.`
