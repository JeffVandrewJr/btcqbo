<h2>Adanced Troubleshooting (only for technical users!)</h2>

There are a couple of advanced torubleshooting tools for more adventurous technical users.

The first is the CLI tool.

You can run a manual QBO token refresh:
```
$ sudo docker exec -it generated_btcqbo_1 /bin/sh
# python3 cli.py refresh
# exit
```
Status of the refresh will print to screen.

If you want to print your current stored QBO API Client ID to screen, try:
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
