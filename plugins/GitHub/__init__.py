from ircbot import Plugin
import re
import requests
import time


class GitHub(Plugin):
    def init(self):
        self.get_config().setdefault("repos", {})
        self.get_config().setdefault("api_key", "")
        self.get_bot().on_chatmessage.subscribe(self.on_chatmessage)

    def on_chatmessage(self, message):
        matches = re.finditer(r"#(\d+)", message.text)
        for match in matches:
            print(match)
            issue_number = match.group(1)
            issue = self.get_issue_data(message.channel, issue_number)
            if issue is None:
                return

            msg = "{title}: {url}".format(**issue)
            self.get_bot().say(message.channel, msg)
            time.sleep(1)

    def get_issue_data(self, channel, issue_number):
        type = self.get_issue_type(channel, issue_number)
        if type is None:
            return

        repo = self.get_repo(channel)
        if repo is None:
            return None

        query = """
        {{
            repository(owner: "{repo_owner}", name: "{repo_name}") {{
                {type}(number: {issue_number}) {{
                    title
                    url
                }}
            }}
        }}
        """.format(type=type, repo_owner=repo["owner"], repo_name=repo["name"],
                   issue_number=issue_number)
        result = self.run_query(query)
        if (result is None or result["data"] is None or
                result["data"]["repository"] is None or
                result["data"]["repository"][type] is None):
            return None

        return result["data"]["repository"][type]

    def get_issue_type(self, channel, issue_number):
        repo = self.get_repo(channel)
        if repo is None:
            return None

        query = """
        {{
            repository(owner: "{repo_owner}", name: "{repo_name}") {{
                issueOrPullRequest(number: {issue_number}) {{
                    __typename
                }}
            }}
        }}
        """
        result = self.run_query(
            query.format(repo_owner=repo["owner"], repo_name=repo["name"],
                         issue_number=issue_number))

        if (result is None or result["data"] is None or
                result["data"]["repository"] is None or
                result["data"]["repository"]["issueOrPullRequest"] is None):
            return None

        typename = (result["data"]["repository"]
                    ["issueOrPullRequest"]["__typename"])
        if typename == "Issue":
            return "issue"
        else:
            return "pullRequest"

    def run_query(self, query):
        api_key = self.get_config().get("api_key", None)
        if api_key is None or api_key.strip() == "":
            return

        headers = {
            "Authorization": "Bearer {}".format(api_key)
        }

        request = requests.post("https://api.github.com/graphql",
                                json={"query": query}, headers=headers)

        if request.status_code == 200:
            return request.json()
        else:
            print("GitHub API request failed with {}"
                  .format(request.status_code))
            return None

    def get_repo(self, channel):
        repos = self.get_config().get("repos")
        if channel not in repos:
            return None

        name_with_owner = repos[channel]
        info = name_with_owner.split("/")
        return {
            "owner": info[0],
            "name": info[1]
        }
