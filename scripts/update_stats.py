import re
import urllib.request
import json
import os

USERNAME = "debugging03"

def get_stats():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    
    pub_repos = 9
    commits_count = 218

    if token:
        query = """
        query {
          user(login: "%s") {
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
            publicRepos: repositories(privacy: PUBLIC, ownerAffiliations: OWNER) {
              totalCount
            }
          }
        }
        """ % USERNAME

        data = json.dumps({"query": query}).encode("utf-8")
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=data,
            headers={
                "Authorization": f"bearer {token}",
                "User-Agent": "Python-Script",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                user_data = result.get("data", {}).get("user", {})
                contributions = user_data.get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions")
                pub = user_data.get("publicRepos", {}).get("totalCount")

                if contributions is not None:
                    commits_count = contributions
                if pub is not None:
                    pub_repos = pub
        except Exception as e:
            print(f"GraphQL API error: {e}")
    else:
        print("No token provided, using current fallback values.")

    return pub_repos, commits_count

def update_readme():
    pub_repos, commits_count = get_stats()
    print(f"Public Repos Count: {pub_repos}")
    print(f"Live Contributions/Commits Count: {commits_count}")

    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if not os.path.exists(readme_path):
        readme_path = "README.md"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update Commits badge with + sign (URL encoded as %2B)
    content = re.sub(
        r'!\[Commits\]\(https://img\.shields\.io/badge/Commits-\d+(?:%2B|\+)?-58A6FF\?style=flat\)',
        f'![Commits](https://img.shields.io/badge/Commits-{commits_count}%2B-58A6FF?style=flat)',
        content
    )

    # Update Public Repos badge
    content = re.sub(
        r'!\[Public Repos\]\(https://img\.shields\.io/badge/Public_Repos-\d+(?:%2B|\+)?-58A6FF\?style=flat\)',
        f'![Public Repos](https://img.shields.io/badge/Public_Repos-{pub_repos}-58A6FF?style=flat)',
        content
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md stats updated successfully!")

if __name__ == "__main__":
    update_readme()
