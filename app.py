"""
Zoom's Webinar Setting Updater
"""
from time import sleep

import requests
from ruamel.yaml import YAML


class Account:
    def __init__(self, token, webinar_ids):
        self.token = token
        self.webinar_ids = webinar_ids

    @property
    def headers(self):
        return {
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
        }

    @classmethod
    def from_yaml_text(cls, content):
        yaml = YAML(typ="safe")
        res = yaml.load(content)

        accounts = []
        for acc in res:
            accounts.append(cls(acc["token"], acc["webinar-ids"]))

        return accounts


ZOOM_API_BASE_URL = "https://api.zoom.us/v2"


def update_cots2021_registration_questions(account):
    """
    Update the registration questions for the webinars.

    See https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrantquestionupdate
    """

    payload = {
        "questions": [
            {
                "field_name": "last_name",
                "required": True,
            },
            {
                "field_name": "org",
                "required": True,
            },
            {
                "field_name": "job_title",
                "required": True,
            },
        ],
        "custom_questions": [
            {
                "title": "Where do you learn about COTS 2021?",
                "type": "multiple",
                "required": True,
                "answers": [
                    "Facebook",
                    "Instagram",
                    "Twitter",
                    "Email",
                    "Newsletters",
                    "Friends",
                    "Other",
                ],
            }
        ],
    }

    for wid in account.webinar_ids:
        print(f"Updating registration questions for {wid} ...", end=" ")
        res = requests.patch(
            ZOOM_API_BASE_URL + "/webinars/{wid}/registrants/questions".format(wid=wid),
            json=payload,
            headers=account.headers,
        )
        print(res.status_code)
        sleep(5)


def update_cots20201_email_settings(account):
    """
    Update the email settings of the webinars.

    See https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarupdate
    """
    payload = {
        "settings": {
            "attendees_and_panelists_reminder_email_notification": {
                "enable": True,
                "type": 7,
            }
        }
    }

    for wid in account.webinar_ids:
        print(f"Update email settings for {wid} ...", end=" ")
        res = requests.patch(
            ZOOM_API_BASE_URL + "/webinars/{wid}".format(wid=wid),
            json=payload,
            headers=account.headers,
        )
        print(res.status_code)
        sleep(5)


def update_qa(account):
    """
    Update the Q&A of webinar(s).

    See https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarupdate
    """
    payload = {
        "settings": {
            "question_and_answer": {
                "enable": True,
                "allow_anonymous_questions": False,
                "answer_questions": "all",
                "attendees_can_upvote": True,
                "attendees_can_comment": True,
            }
        }
    }

    for wid in account.webinar_ids:
        print(f"Update q&a settings for {wid} ...", end=" ")
        res = requests.patch(
            ZOOM_API_BASE_URL + "/webinars/{wid}".format(wid=wid),
            json=payload,
            headers=account.headers,
        )
        print(res.status_code)
        sleep(5)


def create_poll(account):
    """
    Create poll for the webinar(s).

    See https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpollcreate
    """
    payload = {
        "title": "Where are you attending this panel from?",
        "anonymous": False,
        "poll_type": 1,
        "questions": [{"name": "", "type": "single", "answers": ["A", "B"]}],
    }
    for wid in account.webinar_ids:
        print(f"Update email settings for {wid} ...", end=" ")
        res = requests.patch(
            ZOOM_API_BASE_URL + "/webinars/{wid}/polls".format(wid=wid),
            json=payload,
            headers=account.headers,
        )
        print(res.status_code)
        sleep(5)


if __name__ == "__main__":
    from pathlib import Path
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "op",
        help="Operation to perform.",
        choices=(
            "update-registration-question",
            "update-email-setting",
            "create-poll",
            "update-qa-setting",
        ),
    )
    parser.add_argument(
        "--config", help="Path to the configuration file.", default="./config.yaml"
    )

    args = parser.parse_args()

    config_path = Path(args.config)

    if not config_path.exists():
        print(
            "[error] Cannot find a configuration file. We expected it to be at ./config.yaml"
        )
        sys.exit(1)

    with open(str(config_path), "r") as f:
        content = f.read()
        accounts = Account.from_yaml_text(content)

        print("Found {} account(s)".format(len(accounts)))

        if args.op == "update-registration-question":
            print("Updating registration questions")
            for acc in accounts:
                update_cots2021_registration_questions(acc)

        elif args.op == "update-email-setting":
            print("Updating email setting")
            for acc in accounts:
                update_cots20201_email_settings(acc)

        elif args.op == "create-poll":
            print("Creating poll")
            for acc in accounts:
                pass
                # create_cots2021_poll(acc)
        elif args.op == "update-qa-setting":
            print("Updating Q&A setting")
            for acc in accounts:
                update_qa(acc)
