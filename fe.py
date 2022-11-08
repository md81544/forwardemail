#!/usr/bin/env python3
# see https://forwardemail.net/en/email-forwarding-api#create-new-domain-alias

import argparse
import json
import os
import requests
import sys

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
parser.add_argument('-a', '--action', type=str, required=True,
    choices=['add', 'delete', 'list', 'update'])
parser.add_argument('-d', '--domain', type=str, required=True)
parser.add_argument('-e', '--email', type=str, required=False, help="Don't add the @.* portion!")
parser.add_argument('-j', '--json', action='store_true', help='Output full JSON results')
parser.add_argument('--enable', action='store_true', help='Create enabled email address')

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
    # Add new email address:
    json_data = {
        'name': args.email,
        'recipients': real_email,
        'description': 'Added via API',
        'is_enabled': True if args.enable else False
    }
    response = requests.post(
        f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases",
        json = json_data,
        auth = (auth_code, '')
        )
    if response.status_code != 200:
        print(response.json())
        exit(1)

elif args.action == 'update':
    if not args.email:
        print("Please specify email address to update");
        exit(2)
    # Update existing email addresss
    json_data = {
        'recipients': real_email,
        'is_enabled': True if args.enable else False
    }
    response = requests.put(
        f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases/{args.email}",
        json = json_data,
        auth = (auth_code, '')
        )
    if response.status_code != 200:
        print(response.json())
        exit(1)

elif args.action == 'delete':
    if not args.email:
        print("Please specify email address to delete");
        exit(2)
    response = requests.delete(
        f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases/{args.email}",
        auth = (auth_code, '')
        )
    if response.status_code != 200:
        print(response.json())
        exit(1)

elif args.action == 'list':
    req = f"https://api.forwardemail.net/v1/domains/{args.domain}/aliases"
    response = requests.get(req, auth=(auth_code, ''))
    if response.status_code != 200:
        print(response.json())
        exit(1)
    if args.json:
        print(json.dumps(response.json(), indent=2))
        exit(0)
    for alias in response.json():
        if alias["is_enabled"]:
            print("Enabled : ", end='')
        else:
            print("Disabled: ", end='')
        print(f"{alias['name']}@{alias['domain']['name']} --> ", end='')
        list_emails(alias['recipients'])
    if args.email:
        print(f"\nWarning: email parameter \"{args.email}\" was ignored", file=sys.stderr)

else:
    print("Unsupported action")

exit(0)