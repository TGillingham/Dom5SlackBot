import argparse
import datetime
import json
import os
import subprocess

GAMES_DIR = 'games'
LOG_FILE = 'log.txt'

SLACK_CHAT_POST_MESSAGE = 'https://slack.com/api/chat.postMessage'

def launch_host(args, channel, thread_ts):
    dominions_command = [
        args.exe,
        '-S', # server
        '--port', str(args.port),
        '--postexec', 'dom5slackbot.py postexec %s --token %s --channel %s --thread_ts %s' % (args.name, args.token, channel, thread_ts),
        args.name
    ] + args.dom5args
    subprocess.run(dominions_command)

def slack_post_message(args, message, thread_ts=None):
    curl_command = [
        'curl',
        '-s',
        '-F', 'token=%s' % args.token,
        '-F', 'text=%s' % message,
        '-F', 'channel=%s' % args.channel,
        SLACK_CHAT_POST_MESSAGE
    ]
    if thread_ts:
        curl_command += ['-F', 'thread_ts=%s' % thread_ts]
    result = subprocess.run(curl_command, stdout=subprocess.PIPE)
    return json.loads(result.stdout)

def game_dir(args):
    return os.path.join(GAMES_DIR, args.name)

def game_info_path(args):
    return os.path.join(game_dir(args), 'info.json')

def game_log_path(args):
    return os.path.join(game_dir(args), 'log.txt')

def create(args):
    if not args.channel:
        args.channel = args.channel_file.read()

    try:
        os.makedirs(game_dir(args))
    except FileExistsError:
        if not args.force:
            raise

    with open(game_log_path(args), 'w') as log:
        log.write('Created at %s\n' % str(datetime.datetime.now()))
        post = slack_post_message(
            args,
            'A game named "%s" is ready to join on port %i' % (args.name, args.port)
        )
        log.write(json.dumps(post))
        log.write('\n')

        if post['ok']:
            thread_ts = post['ts']
            info = {
                'channel': args.channel,
                'thread_ts': thread_ts,
            }
            with open(game_info_path(args), 'w') as info_file:
                info_file.write(json.dumps(info))

            launch_host(args, info['channel'], info['thread_ts'])
        else:
            log.write('Failed to post message. Response:\n%s' % json.dumps(post))


def host(args):
    with open(game_info_path(args), 'r') as info_file:
        info = json.loads(info_file.read())

    with open(game_log_path(args), 'a') as log:
        log.write('Hosting at %s\n' % str(datetime.datetime.now()))

    launch_host(args, info['channel'], info['thread_ts'])

def postexec(args):
    with open(game_log_path(args), 'a') as log:
        log.write('%s\n' % str(datetime.datetime.now()))
        post = slack_post_message(args, '%s: A new turn is ready!' % args.name, thread_ts=args.thread_ts)
        log.write(json.dumps(post))
        log.write('\n')

def hosting_func(func):
    def f(args):
        func(args)
    return f

def slack_func(func):
    def f(args):
        if not args.token:
            args.token = args.token_file.read()
        func(args)
    return f

def add_hosting_args(parser):
    parser.add_argument('name')
    parser.add_argument('port', type=int)
    parser.add_argument('--exe', default=os.path.join(
        os.environ["ProgramFiles(X86)"],
        "Steam",
        "steamapps",
        "common",
        "Dominions5",
        "Dominions5.exe"
    ))
    parser.add_argument('dom5args', nargs='*')

def add_slack_args(parser):
    parser.add_argument('--token')
    parser.add_argument('--token-file', default='token.txt', type=argparse.FileType('r'))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create')
    add_hosting_args(parser_create)
    add_slack_args(parser_create)
    parser_create.add_argument('--channel')
    parser_create.add_argument('--channel-file', default='channel.txt', type=argparse.FileType('r'))
    parser_create.add_argument('-f', '--force', action='store_true')
    parser_create.set_defaults(func=slack_func(hosting_func(create)))

    parser_host = subparsers.add_parser('host')
    add_hosting_args(parser_host)
    add_slack_args(parser_host)
    parser_host.set_defaults(func=slack_func(hosting_func(host)))

    parser_postexec = subparsers.add_parser('postexec')
    parser_postexec.add_argument('name')
    parser_postexec.add_argument('--channel', required=True)
    parser_postexec.add_argument('--thread_ts', required=True)
    parser_postexec.add_argument('--token', required=True)
    parser_postexec.set_defaults(func=postexec)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
