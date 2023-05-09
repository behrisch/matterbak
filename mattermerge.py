#!/usr/bin/env python3
"""
mattermerge merges multiple backups done with matterbak into a jsonl file
usable by the mattermost bulk import
https://docs.mattermost.com/onboard/bulk-loading-data.html#data-format
"""
import argparse
import json
import zipfile

def main():
    """Main function, also entry point for the matterbak script"""
    parser = argparse.ArgumentParser()
    parser.add_argument("zips", nargs="+",
                        help="input zip files")
    parser.add_argument("-o", "--output", default="matter.jsonl",
                        help="jsonl file to write, default is 'matter.jsonl'")
    parser.add_argument("-a", "--attachments", action="store_true", default=False,
                        help="include also attachments")
    options = parser.parse_args()
    zips = [zipfile.ZipFile(z) for z in options.zips]
    with open(options.output, "w", encoding="utf8") as jsonl:
        json.dump({ "type": "version", "version": 1}, jsonl)
        print(file=jsonl)
        teams = {}
        for z in zips:
            for n in z.namelist():
                if n.startswith("teams/"):
                    team = json.load(z.open(n))
                    if team["id"] in teams:
                        continue
                    teams[team["id"]] = team["name"]
                    keys = ("name", "display_name", "type", "description", "allow_open_invite")
                    json.dump({ "type": "team", "team": {key: team[key] for key in keys}}, jsonl)
                    print(file=jsonl)
        for z in zips:
            for n in z.namelist():
                if n.startswith("channels/") and n.count("/") == 1:
                    channel = json.load(z.open(n))
                    chnl = {key: channel[key] for key in ("name", "display_name", "type", "header", "purpose")}
                    chnl["team"] = teams.get(channel["team_id"], "")
                    json.dump({ "type": "channel", "channel": chnl}, jsonl)
                    print(file=jsonl)


if __name__ == "__main__":
    main()
