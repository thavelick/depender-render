# Depender Render
Depender Render is a simple tool to render a dependency graph for you github issues.

## Installation
```bash
git clone https://github.com/thavelick/depender-render.git
pip install -r requirements.txt
```

## Usage
```
usage: depender_render.py [-h] -u USER -r REPO [--parent-issue PARENT_ISSUE]
                          [--output OUTPUT]

arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Github user
  -r REPO, --repo REPO  Github repo
  --parent-issue PARENT_ISSUE
                        Parent issue number
  --output OUTPUT       Output file
```

## Example

```bash
./depender_render.py -u thavelick -r depender-render --parent-issue=1 graph.svg
```

The above will:
1. fetch issue #1 from `thavelick/depender-render/issues`
2. parse the issue description for any issues that are linked
3. fetch those issues
4. parse the issue description for any issues that are linked with "depends on", or "requires" like:
    * `depends on #2` or
    * `requires https://github.com/thavelick/depender-render/issues/3`
5. Recursively fetch those issues adding them to the graph
6. render the dependency graph to `graph.svg`

## Dependencies
* Python 3.8+
* graphviz

That's it!

## Design Guidlines
* Use urllib to fetch issues from github