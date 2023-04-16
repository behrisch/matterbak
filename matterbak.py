import argparse
import json
import os
import mattermost

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", default="credentials.json")
    parser.add_argument("--backup-user")
    options = parser.parse_args()
    with open(options.credentials, encoding="utf8") as cred_file:
        creds = json.load(cred_file)
    if options.backup_user is None:
        options.backup_user = creds["user"]
    matter = mattermost.MMApi(creds["url"])
    matter.login(creds["user"], creds["password"])
    for cat in ("teams", "channels", "users"):
        os.makedirs(cat, exist_ok=True)
    user = matter.get_user_by_username(options.backup_user)
    with open(os.path.join("users", user["id"] + ".json"), "w", encoding="utf8") as desc:
        json.dump(user, desc)
    channels = []
    for team in matter.get_teams():
        members = set([m["user_id"] for m in matter.get_team_members(team["id"])])
        if user["id"] in members:
            os.makedirs(os.path.join("teams", team["id"]), exist_ok=True)
            with open(os.path.join("teams", team["id"] + ".json"), "w", encoding="utf8") as desc:
                json.dump(team, desc)
            channels += list(matter.get_channels_for_user(user["id"], team["id"]))
    for chnl in channels:
        os.makedirs(os.path.join("channels", chnl["id"]), exist_ok=True)
        with open(os.path.join("channels", chnl["id"] + ".json"), "w", encoding="utf8") as desc:
            json.dump(chnl, desc)
        for post in matter.get_posts_for_channel(chnl["id"]):
            post_file = os.path.join("channels", chnl["id"], post["id"] + ".json")
            if not os.path.exists(post_file):
                with open(post_file, "w", encoding="utf8") as desc:
                    json.dump(post, desc)
            user_file = os.path.join("users", post["user_id"] + ".json")
            if not os.path.exists(user_file):
                with open(user_file, "w", encoding="utf8") as desc:
                    json.dump(matter.get_user(post["user_id"]), desc)


if __name__ == "__main__":
    main()
