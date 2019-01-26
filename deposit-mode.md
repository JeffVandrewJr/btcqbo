<h1>Deposit Mode</h1>

<h2>What This Plugin Does and Does Not Do</h2>

**What it does do:**

* Records customer payments as deposits in Quickbooks

* Separates revenue from sales tax, and records revenue separately from sales tax

**What it does not do:**

* Automatically calculate sales tax. There are hundreds of different sales tax jurisdictions in the USA alone, each with its own rates and definitions. BTCPay is not sales tax software. It simply takes the revenue/sales tax breakdown from your e-commerce solution and accepts it as correct. If you need a software solution that automatically tracks rates for all of the US jursdictions, you need to integrate a solution like TaxJar of Avalara into your e-commerce site. If Avalara or TaxJar are calculating your sales tax on your e-commerce site, you can then pass the revenue/sales tax breakdown to this plugin and it will work correctly.

* Integrate the Quickbooks Sales Tax Module. This plugin records all revenue to an Income account on your P&L called "BTCPay Sales." It records all sales tax collected into a Liability account on your balance sheet called "Sales Tax from BTCPay." When you pay your sales tax each month, you'd post a regular check to "Sales Tax from BTCPay." This is a very straightforward solution. You would not record sales tax in Quickbooks through the sales tax module, because as referenced above BTCPay does not store jurisdiction information and therefore cannot integrate native Quickbooks sales tax. If you need direct integration into the Quickbooks Sales Tax module, you should skip using this plugin and instead integrate your e-commerce solution directly into the Quickbooks API.

<h2>Notes</h2>

If you collect sales tax, you must make use of the new `taxIncluded` invoice field within BTCPay. You may need to update BTCPay if you're using an older version.

In BTCPay, `price` is inclusive of tax. So if you're creating an invoice for $100 in a jursidiction with 7% sales tax, you would pass BTCPay a `price` of $107 (not $100) and `taxIncluded` of $7.

All payments made through BTCPay will be recorded in QBO in an "Other Current Asset" account called "BTCPay-Bitcoin." They are recorded at USD value as of the date the invoice was paid. This is not a bug; it is intentional behavior. The USD value on the payment date is the amount of taxable income recognized as well as the tax basis for a future sale of BTC under US Tax law, so the BTC is recorded in QBO accordingly. The information herein is educational only and is not tax advice; consult your tax professional.

Payments will not record in QBO until the invoice status in BTCPay is "confirmed." Payments are considered "confirmed" based on your BTCPay settings. The default is one on-chain confirmation.

<h2>Activation</h2>

SSH into your BTCPay server, and then run the following commands:

```bash
# Log in as root and load environment variables of BTCPayServer
sudo su -

# go into the BTCPay-Docker directory
cd btcpay-docker

# Add this plugin docker fragment
export BTCPAYGEN_ADDITIONAL_FRAGMENTS="$BTCPAYGEN_ADDITIONAL_FRAGMENTS;opt-add-btcqbo"

# Save
. btcpay-setup.sh -i
```

<h3>Post-Activation</h3>

After activation, you can access the plugin directly from within BTCPay under Server Settings/Services, or alternatively at https://btcpay.example.com/btcqbo, replacing btcpay.example.com with the domain where your BTCPay instance is hosted. On the plugin welcome screen, there will be buttons for:

* Entering Intuit API Keys
* Syncing the plugin to QBO
* Syncing the plugin to BTCPay

<h3>Entering Intuit API Keys</h3>

You need API keys from Intuit to sync to Quickbooks Online.

1. Head to https://developer.intuit.com and log in using the same login you normally use for Quickbooks Online. Your account will then be granted developer privileges.

2. After logging in, click on "My Apps" and create a new app. Call the app "BTCQBO". Whenever Intuit asks, you need access to the Accounting API (not the Payments API).

3. After the "app" is created, click "Keys". There will be sandbox and production keys. To obtain the production keys, Intuit will require you to fully fill out your developer profile. Intuit will also require links to your privacy policy and EULA; these are largely irrelevant since your own business will the only "user" of your app. If you don't have links to a EULA and privacy policy, you may choose to use these links https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/privacy-sample and https://raw.githubusercontent.com/JeffVandrewJr/btcqbo/master/eula-sample. These are provided for educational purposes, and consult with your own attorney if you have questions. 

4. On the Intuit Developer site, underneath your Intuit "production" keys, add "https://btcpay.example.com/btcqbo/qbologged" as a redirect URI, replacing btcpay.example.com with the domain where your BTCPay instance is hosted. Ensure you're doing this in the "production" (not sandbox) area of the page.

5. From the plugin welcome screen, click the button to enter your Intuit API Keys. Enter your Quickbooks Client ID and Quickbooks Client Secret obtained from the Intuit Developer site above. Be sure to use the "Production" rather than "Sandbox" keys (unless you are in fact running on a sandbox test company).

<h3>Syncing QBO</h3>

After entering your Intuit API keys into the plugin, you'll be automatically redirected to sync the plugin to QBO. (If you need to resync later without updating your API keys, from the plugin welcome screen, you can hit the button to sync QBO.) Follow the on-screen instructions to sync to Inuit; you'll need your QBO username and password. You can repeat this step at any time in the future if you become unsynced from Intuit for any reason.

<h3>Syncing BTCPay</h3>

From the plugin welcome screen, hit the button to sync BTCPay. Click on the link provided to obtain a pairing code from your BTCPay Server instance. Then enter the pairing code in the plugin, and submit.


<h4>Troubleshooting (only for technical users!)</h4>

If you are a more technical user, there are some advanced troubleshooting and testing tools explained in the advanced_troubleshooting.md file.
