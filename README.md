<h1>Quickbooks Online Connector for BTCPay Server</h1>

Copyright (C) 2018 Jeff Vandrew Jr

<h2>Introduction</h2>

Quickbooks Online (QBO) is currently the most popular small business bookkeeping solution, and is often used as an online invoicing solution. When customers receive an online invoice from a business using QBO, they currently have the option to pay electronically using credit card or ACH (via integrated Intuit Payments) or Bitcoin (via Intuit PayByCoin, which unfortunately only supports Bitpay and Coinbase). This software extends Quickbooks Online to take payments through BTCPay server. It is self-hosted and does not rely on any third party.

When this plugin is installed, customers choosing to pay a QBO invoice using BTCPay automatically have a BTCPay invoice generated with the customer's data pre-filled, and payments to the BTCPay invoice are autmatically recorded in QBO. Before generating the invoice, the software verifies that the email and invoice number match to prevent against customer typos.

<h2>Known Issues</h2>

Unfortunately the Quickbooks API does not allow emailing customer receipts. BTCPay does not support this either, leaving the feature to merchant software. Assuming there are no plans for BTCPay to support this feature, I will implement this in the plugin in the near future.

<h2>Notes</h2>

All payments made through BTCPay will be recorded in QBO in an "Other Current Asset" account called "Bitcoin." They are recorded at USD value as of the date the invoice was paid. This is not a bug; it is intentional behavior. The USD value on the payment date is the amount of taxable income recognized as well as the tax basis for a future sale of BTC under US Tax law, so the BTC is recorded in QBO accordingly. The information herein is educational only and is not tax advice; consult your tax professional.

Payments will not record in QBO until the invoice status in BTCPay is "confirmed." Payments are considered "confirmed" based on your BTCPay settings. The default is one on-chain confirmation.

<h2>Installation</h2>

Instructions assume that you are using the Dockerized BTCPay Server, which would be the case if you originally used the one-click install through LunaNode.

1. Log into your LunaNode or other VPS via SSH.

2. `$ sudo su -` THE TRAILING DASH IS CRITICALLY IMPORTANT. You may wipe your data if you do an install after running the command without the trailing dash.

3. `# cd btcpayserver-docker`

4. `# btcpay-update.sh`

4. `# export BTCPAYGEN_ADDITIONAL_FRAGMENTS="$BTCPAYGEN_ADDITIONAL_FRAGMENTS;opt-add-btcqbo"`

5. `# . btcpay-setup.sh -i`

6. `# exit`

You only need to do this once, as going forward the plugin should update automatically when you update BTCPay.

<h3>Obtain Intuit Keys</h3>

You need API keys from Intuit to sync to Quickbooks Online.

1. Head to https://developer.intuit.com and log in using the same login you normally use for Quickbooks Online. Your account will then be granted developer privileges.

2. After logging in, clock on "My Apps" and create a new app. The title is irrelevant.

3. After the "app" is created, click "Keys". There will be sandbox and production keys. To obtain the production keys, Intuit will require you to fully fill out your developer profile. Intuit will also require links to your privacy policy and EULA; these are largely irrelevant since your own business will the only "user" of your app. If you don't have links to a EULA and privacy policy, you may choose to use these links https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/privacy-sample and https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/eula-sample. These are provided for educational purposes, and consult with your own attorney if you have questions. 

4. On the Intuit Developer site, underneath your Intuit "production" keys, add "https://btcpay.example.com/btcqbo/qbologged" as a redirect URI, replacing btcpay.example.com with the domain where your BTCPay instance is hosted. Ensure you're doing this in the "production" (not sandbox) area of the page.

<h3>Syncing QBO & BTCPay to the Plugin</h3>

1. From a web browser, visit https://btcpay.example.com/btcqbo/setkeys, replacing btcqbo.example.com with your domain. Enter your Quickbooks Client ID and Quickbooks Client Secret obtained from the Intuit Developer in Part 1. Be sure to use the "Production" rather than "Sandbox" keys (unless you are in fact running on a sandbox test company.

2. From a web browser, visit https://btcpay.example.com/btcqbo/authqbo, replacing btcqbo.example.com with your domain. Login with the username and password that you set above.

3. Follow the steps to sync to Inuit.

4. Go log into your BTCPay server, click on your store, and then hit settings. From the settings menu, create an authorization token. Once the token is created, BTCPay will provide a pairing code.

5. From a web browser, visit https://btcpay.example.com/btcqbo/authbtc, replacing btcqbo.example.com with your domain. Enter the pairing code from the step above, and submit.

<h3>Creating Public Facing Payment Portal</h3>

You also need a page on your business' website to which your Quickbooks invoices can link. You'll also need to edit your Quickbooks templates so that customers know they can pay in Bitcoin! This section will show you how.

These instructions assume your business' normal public facing site is a Wordpress site. 

1. In Quickbooks Online, edit your outgoing email template for invoicing (Gear Icon --> Account & Settings --> Sales --> Messages) with a concluding paragraph like this one:
```
"Click "Review and Pay below to pay via ACH or Credit Card, or click https://yourdomain.com/pay to pay via Bitcoin.
```
Also edit your Quickbooks Online invoice template. To get there, in Quickbooks Online, click the gear icon, then Custom Form Styles, then hit "Edit" next your current form style. Then click the block that says "Content". The sample invoice will then become clickable. Click on the bottom content block (where it says "Total Due"). A "Message to Customer" field will then appear. In that field, type:
```
Head to https://yourdomain.com/pay to pay via Bitcoin.
```
Set the font size, and then don't forget to hit "Done" to save your changes in Quickbooks Online.

2. Log into your Wordpress site and create a new page. Title the new page "Make a Bitcoin Payment". Set the URL to match the one you chose in Step 1 (ex: yourdomain.com/pay).

3. Paste the code below into the body:
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
In the code, change `btcpay.example.com` to the domain of your BTCPay host (but leave all portions of the URL following the ".com" the same). Also set the redirect URL of your choice. Save the page in Wordpress; due to the magic of CSS it should automatically be styled to match your site.

<h4>Troubleshooting (only for technical users!)</h4>

If QBO becomes unsynced, try running:
```
$ sudo docker exec -it generated_btcqbo_1 /bin/sh
# python3 cli.py refresh
# exit
```
If the screen prints a bunch of JSON data, you've successfully resynced. If not, you may have to reauthorize from the web interface.

If you are familiar with RQ, you can view the RQ dashboard at https://btcpay.example.com/btcqbo/rq (replacing with your own domain).
