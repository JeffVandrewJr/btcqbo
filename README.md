<h1>Quickbooks Online Connector for BTCPay Server</h1>

Copyright (C) 2018 Jeff Vandrew Jr

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
 
<h2>Introduction</h2>
 
Quickbooks Online (QBO) is currently the most popular small business bookkeeping solution, and is often used as an online invoicing solution. When customers receive an online invoice from a business using QBO, they currently have the option to pay electronically using credit card or ACH (via integrated Intuit Payments) or Bitcoin (via Intuit PayByCoin, which unfortunately only supports BitPay and Coinbase). This software extends Quickbooks Online to take payments through BTCPay server.

Customers choosing to pay a QBO invoice using BTCPay automatically have a BTCPay invoice generated with the customer's data pre-filled, and payments to the BTCPay invoice are autmatically recorded in QBO.

<h2>Installation</h2>

This install documentation is sparse and will be improved over the coming weeks!

Below are installation instructions for deployment on a Linux server or VPS separate from your BTCPay Server instance. Deployment is also possible in a Docker container residing on the same server with BTCPay; instructions are forthcoming for users wanting to deploy a dockerized BTCQBO instance alongside the dockerized BTCPay server created with one click on LunaNode.

<h3>Part 1: Obtain Intuit Keys</h3>

1. Head to https://developer.intuit.com and log in using the same login you normally use for Quickbooks Online. Your account will then be granted developer privileges.

2. After logging in, clock on "My Apps" and create a new app. The title is irrelevant.

3. After teh app is created, click "Keys". There will be sandbox and production keys. To obtain the production keys, Intuit will require you to fully fill out your developer profile. Intuit will also require links to your privacy policy; these are largely irrelevant since your own business will the only "user" of your app. If you don't have a privacy policy on your site, here's a sample: https://www.bbb.org/greater-san-francisco/for-businesses/toolkits1/sample-privacy-policy/

4. Select a new subdomain for the connector. If your company's main site is example.com, you may wish to use btcqbo.example.com. This won't be a customer-facing site, so choice doesn't much matter. Set the DNS record for this subdomain to point to the public IP address of the server you're using for deployment. Underneath your Intuit keys, add "https://btcqbo.example.com:8000/qbologged" as a redirect URI, replacing btcqbo.example.com with your domain.

<h3>Part 2: Install BTCQBO</h3>

1. Using your distribution's package manager, install redis-server, python3, python3-venv, python3-dev, and nginx.

2. Using systemd, enable redis-server.service, then start redis-server.service. Do the same for nginx.

3. Using git, clone this repository to a local folder.

4. From the cloned repository folder, create a python venv ($ python3 -m venv venv). Then activate the venv ($ source venv/bin/activate).

5. Install dependencies by running:
$ sudo pip install -r requirements.txt

6. Create an .env file. A form template is provided as env.sample. Be sure to enter your "client ID" and "client secret" from the keys tab on the Intuit Developer site. Also change the callback URL to the URL you chose in the last step of Part 1. Finally, change the BTCPay server URL to the URL of your BTCPay instance. SECRET_KEY can remain all zeroes as the this site will not be public facing after syncing is complete.

7. Enable systemd unit files for btcqbo.service and rq-worker.service. Sample templates for both are provided which use standard LunaNode VPS file paths; you will need to edit the file paths accordingly for your installation. After enabling the unit files, be sure to start them.

8. Go to /etc/nginx/sites-enabled and remove the "default" file. Create a file named "btcqbo". A sample of what should be included in that file is provided in this repository as "btcqbo.nginx.conf". [Note that the file name in /etc/nginx/sites-enabled should simply be "btcqbo".]

9. $ sudo service nginx reload

<h3>Part 3: Sync with Intuit & BTCPay</h3>

1. From a web browser, visit https://btcqbo.example.com:8000/authqbo, replacing btcqbo.example.com with your domain.

2. Follow the steps to sync to Inuit.

3. Go log into your BTCPay server, click on your store, and then hit settings. From the settings menu, create an authorization token. Once the token is created, BTCPay will provide a pairing code.

4. From a web browser, visit https://btcqbo.example.com:8000/authbtc, replacing btcqbo.example.com with your domain. Enter the pairing code from the step above, and submit.

5. Disable public access by editing your .env file to change AUTH_ACCESS to false. The restart btcqbo.service for the change to take effect.

<h3>Part 4: The Public Facing Payment Portal</h3>

These instructions assume your business' public facing page is a wordpress site. 

1. From within BTCPay, click "Apps", then create a new POS app. Scroll to the sample code at the bottom, and note the URL given on the <form method="POST" action section.

2. Create a new page on your wordpress site. Title it "Make a Bitcoin Payment". Set the URL so to something short, like example.com/pay.

3. Paste the code below into the body:
`<form method="POST" action="ENTER POS URL HERE">
USD Amount:
  <input type="text" name="amount" />
Email Address:
  <input type="text" name="email" />
Invoice Number:
  <input type="text" name="orderId" />
  <input type="hidden" name="notificationUrl" value="https://btcqbo.example.com:8000/api/v1/payment" />
  <input type="hidden" name="redirectUrl" value="https://example.com/thanksyou" />
  <button type="submit">Pay now</button>
</form>`

4. Enter the URL from #3 above as ENTER POS URL HERE. Change btcqbo.example.com to your domain later in the form code. Add a post-payment redirect URL of your choice in the appropriate section.

5. In Quickbooks Online, edit your outgoing email template for invoicing with a concluding paragraph like this one:

"Click "Review and Pay below to pay via ACH or Credit Card, or click https://example.com/pay to bay via Bitcoin.
