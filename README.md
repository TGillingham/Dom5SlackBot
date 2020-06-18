# Dominions 5 Slack Integration

Sends chat messages to Slack to advertise Dominions 5 games and turns.

## Usage

First, [create a Slack app](https://api.slack.com) and obtain an OAuth token. The token will be passed to the script in one of a few ways: by (A) creating a `token.txt` file in the working directory, (B) passing the token file's path to the script with `--token-file`, or (C) passing the token directly to the script with `--token`. Bot tokens require the `chat:write` scope.
Add your Slack app to a channel. Just like the OAuth token, the channel needs to be provided to the script when creating a game.

Start a new game:
```
dom5slackbot.py create
	$NAME
	$PORT
	[--token $TOKEN]
	[--token-file $TOKEN_FILE]
	[--channel $CHANNEL]
	[--channel-file $CHANNEL_FILE]
	[--force]

# $NAME is the name of the game. It will be used as a key for saved information,
#   like the game's save and the script's log file.

# $PORT sets the server's port.

# $TOKEN or $TOKEN_FILE are optional ways to pass your app's OAuth token to the
#   script. Another option is to write it to token.txt in the working directory.

# $CHANNEL, $CHANNEL_FILE, or channel.txt are similar to the OAuth token. You
#   can easily get a channel from the Slack URL (they look like C0123ABC).
```
The app will post a message advertising the game in the specified channel. Whenever a turn is processed, it will reply to the advertisement message to let everybody know that they can take another turn.

This command can also be used to add chat messages to preexisting games. Just close the existing server, then run this command.

If you would like to recreate the saved state for this game, pass `--force`. This is useful when migrating the chat thread to a different channel or making tweaks to the script.

Continue hosting an existing game:
```
dom5slackbot.py host $NAME $PORT
```
