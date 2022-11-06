#!/usr/bin/env python3
# see https://forwardemail.net/en/email-forwarding-api#create-new-domain-alias

import argparse
import json
import os
import requests

auth_code = ''
try:
    with open(os.path.expanduser("~/.fe.cfg"), "r") as f:
        auth_code = f.readline()
        real_email = f.readline()
except IOError:
    print("Could not find file containing API auth code.")
    print("Create a file called ~/.fe.cfg and place your auth code on the first line.");
    print("Place your default 'real' email address on the second line.");
    exit(3)

parser = argparse.ArgumentParser(description='Add disabled email address to forwardemail')
parser.add_argument('-a', '--action', type=str, required=True, choices=['add', 'delete', 'list'])
parser.add_argument('-d', '--domain', type=str, required=True)
parser.add_argument('-e', '--email', type=str, required=False, help="Don't add the @.* portion!")
parser.add_argument('-j', '--json', action='store_true')
args = parser.parse_args()

def list_emails(email_list):
    first = True
    for recipient in email_list:
        if first:
            first = False
        else:
            print(", ")
        print(recipient, end=' ')
        print("")


if args.action == 'add':
    if not args.email:
        print("Please specify email address to add");
        exit(2)
    # Add new, disabled, email address:
    json_data = {
        'name': args.email,
        'recipients': real_email,
        'description': 'Added via API',
        'is_enabled': False
    }
    response = requests.post(
        f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases",
        json = json_data,
        auth = (auth_code, '')
        )
    if response.status_code != 200:
        print(response.json())
        exit(1)

elif args.action == 'delete':
    print("TODO")

elif args.action == 'list':
    req = f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases"
    if args.email:
        req = req + f"/{args.email}"
    response = requests.get(req, auth=(auth_code, ''))
    if response.status_code != 200:
        print(response.json())
        exit(1)
    if args.json:
        print(json.dumps(response.json(), indent=2))
        exit(0)
    if isinstance(response.json(), list):
        for alias in response.json():
            print(f"{alias['name']}@{alias['domain']['name']} --> ", end='')
            list_emails(alias['recipients'])
    else:
        print(f"{response.json()['name']}@{response.json()['domain']['name']} --> ", end='')
        list_emails(response.json()["recipients"])

else:
    print("Unsupported action")

exit(0)