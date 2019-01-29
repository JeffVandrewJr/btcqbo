<h1>Quickbooks Online Connector for BTCPay Server</h1>

Copyright (C) 2018-2019 Jeff Vandrew Jr

Latest Stable Version: 0.3.18

Versions prior to 0.3.13 do not handle lightning payments correctly, so be sure you have installed viersion 0.3.13 or higher if you have lightning active. You can check your version by running `docker ps`.

This plugin for BTCPay Server has two modes of operation:

1. **Invoicing Mode**: If you use Quickbooks Online to send invoices to your customers and want your customers to be able to pay invoices sent from Quickbooks Online in Bitcoin, [click here](https://github.com/JeffVandrewJr/btcqbo/blob/master/invoice-mode.md).

2. **Deposit Mode**: If you do not send customers invoices through Quickbooks Online, but simply want your payments received through BTCPay Server to automatically post to Quickbooks, this mode would be for you. This would be common for online retailers and other businesses receiving payments through e-commerce solutions. [Click here](https://github.com/JeffVandrewJr/btcqbo/blob/master/deposit-mode.md) for setup.
