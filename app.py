import os
from flask import Flask, request, render_template_string
import requests
from jinja2 import Template

app = Flask(__name__)

def fetch_repo_details(repo_url):
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    owner, repo = parts[-2], parts[-1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

def generate_readme(repo_data):
    readme_template = """
# {{ name }}

{{ description }}

## Repository Details

- **Primary Language:** {{ language }}
- **Stars:** {{ stargazers_count }}
- **Forks:** {{ forks_count }}
- **Open Issues:** {{ open_issues_count }}
{% if license %}
- **License:** {{ license.name }}
{% endif %}

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Clone the repository:

~~~bash
git clone {{ html_url }}
~~~

## Usage

Follow the usage instructions provided in the project documentation.

## Contributing

Feel free to fork the project and submit pull requests. For major changes, please open an issue first.

## License

{% if license %}
This project is licensed under the {{ license.name }} license.
{% else %}
No license information provided.
{% endif %}
    """
    template = Template(readme_template)
    return template.render(
        name=repo_data.get("name", "Project Name"),
        description=repo_data.get("description", "No description provided."),
        language=repo_data.get("language", "N/A"),
        stargazers_count=repo_data.get("stargazers_count", 0),
        forks_count=repo_data.get("forks_count", 0),
        open_issues_count=repo_data.get("open_issues_count", 0),
        license=repo_data.get("license", None),
        html_url=repo_data.get("html_url", "")
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        repo_url = request.form.get('repo_url')
        try:
            repo_data = fetch_repo_details(repo_url)
            result = generate_readme(repo_data)
        except Exception as e:
            error = str(e)
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>AutoREADME Generator</title>
</head>
<body>
    <h1>AutoREADME Generator</h1>
    <form method="POST">
        <label for="repo_url">GitHub Repository URL:</label><br>
        <input type="text" id="repo_url" name="repo_url" required style="width:400px;"><br><br>
        <input type="submit" value="Generate README">
    </form>
    {% if result %}
    <h2>Generated README.md</h2>
    <pre>{{ result }}</pre>
    {% elif error %}
    <h2>Error:</h2>
    <p>{{ error }}</p>
    {% endif %}
</body>
</html>
    """, result=result, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, host='0.0.0.0', port=port)
