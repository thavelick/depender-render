#!/bin/python3
"A simple tool Depender Render is a simple tool to render a dependency graph for you github issues."


import argparse
import re
import urllib.request
import urllib.error
import json
import graphviz


def get_issue(user, repo, issue_number):
    """Fetch an issue from github api"""
    url = f"https://api.github.com/repos/{user}/{repo}/issues/{issue_number}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        print(f"Error fetching issue {issue_number}: {error}")
        return None


def get_issues(user, repo, issue_numbers):
    """Fetch a list of issues from github api"""
    return [get_issue(user, repo, issue_number) for issue_number in issue_numbers]


def get_issue_numbers_from_text(user, repo, text):
    """Parse a string for issue numbers.

    Includes issue numbers like `#123` and issue links like
    `http://github.com/user/repo/issues/123`
    """
    issue_numbers = set()
    issue_numbers.update(re.findall(r"#(\d+)", text))
    issue_numbers.update(re.findall(rf"{user}/{repo}/issues/(\d+)", text))
    return issue_numbers


def get_issue_numbers_from_issue(user, repo, issue):
    """Parse an issue for issue numbers"""
    return get_issue_numbers_from_text(user, repo, issue["body"])


def get_issue_numbers_from_issues(user, repo, issues):
    """Parse a list of issues for issue numbers"""
    issue_numbers = set()
    for issue in issues:
        issue_numbers.update(get_issue_numbers_from_issue(user, repo, issue))
    return issue_numbers


DEPENDENCY_KEYWORDS = ["depends on", "requires"]


def get_issue_numbers_from_issue_with_depends_on(user, repo, issue):
    """Parse an issue for issue numbers with "depends on" or "requires"."""
    issue_numbers = set()
    for line in issue["body"].splitlines():
        for keyword in DEPENDENCY_KEYWORDS:
            if keyword in line:
                issue_numbers.update(get_issue_numbers_from_text(user, repo, line))
    return issue_numbers


def get_issue_numbers_from_issues_with_depends_on(user, repo, issues):
    """Parse a list of issues for issue numbers with "depends on" or "requires"."""
    issue_numbers = set()
    for issue in issues:
        issue_numbers.update(
            get_issue_numbers_from_issue_with_depends_on(user, repo, issue)
        )
    return issue_numbers


def get_dependency_graph(user, repo, issue_number):
    """Get a dependency graph for an issue.

    Returns a graphviz.Digraph object.
    """
    graph = graphviz.Digraph()
    graph.attr("node", shape="box")
    graph.attr("edge", arrowhead="vee")

    def get_dependencies(issue_number, max_depth=100):
        """Recursively get dependencies for an issue."""
        if max_depth == 0:
            return
        issue = get_issue(user, repo, issue_number)
        if issue is None:
            return
        graph.node(str(issue["number"]), issue["title"])
        for dependency in get_issue_numbers_from_issue_with_depends_on(
            user, repo, issue
        ):
            graph.edge(str(issue["number"]), str(dependency))
            get_dependencies(dependency, max_depth - 1)

    get_dependencies(issue_number)
    return graph


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-u", "--user", required=True, help="The github user or organization"
    )
    parser.add_argument("-r", "--repo", required=True, help="The github repository")
    parser.add_argument(
        "--parent-issue",
        required=True,
        help="The issue number to start the dependency graph from",
    )
    parser.add_argument("output", help="The output file")
    args = parser.parse_args()

    graph = get_dependency_graph(args.user, args.repo, args.parent_issue)

    # Render the graph to the output file
    graph.render(args.output)


if __name__ == "__main__":
    main()
