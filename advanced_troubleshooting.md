<h2>Adanced Troubleshooting (only for technical users!)</h2>

There are a couple of advanced torubleshooting tools for more adventurous technical users.

The first is the CLI tool.

You can run a manual QBO token refresh:
```
$ sudo docker exec -it generated_btcqbo_1 /bin/sh
# python3 cli.py refresh
# exit
```
If the screen prints a bunch of JSON data, you've successfully refreshed. If not, you may have to reauthorize from the web interface.

If you want to print your current stored QBO API keys and tokens to screen, try:
```
$ sudo docker exec -it generated_btcqbo_1 /bin/sh
# python3 cli.py printqb
# exit
```

If for testing purposes you wish to wipe all QBO data completely, try:
```
$ sudo docker exec -it generated_btcqbo_1 /bin/sh
# python3 cli.py deletekeys
# exit
```

Lastly, if you are familiar with RQ, you can view the RQ dashboard at https://btcpay.example.com/btcqbo/rq (replacing with your own domain). Assuming you have paired with QBO, there should always be a task running on the BTCQBO queue.
