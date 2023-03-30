import tempfile
import zipfile
import os

import requests
import click


@click.command()
@click.argument('token')
@click.option('--org', default='idoven', show_default=True)
def cli(token, org):
    headers = {'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28',
               'Authorization': f"Bearer {token}"}
    r = requests.get(f"https://api.github.com/orgs/{org}/repos", headers=headers)

    if not os.path.exists(f"{os.getcwd()}/code"):
        os.mkdir(f"{os.getcwd()}/code")

    with tempfile.TemporaryDirectory() as temp_dir:
        for repo in r.json():
            print(f"Downloading {repo['name']}")
            res = requests.get(f"https://api.github.com/repos/{org}/{repo['name']}/zipball/main", headers=headers, stream=True)
            if res.status_code == 404:
                print(f"Access denied for {repo['name']}")
            else:
                with open(f"{temp_dir}/{repo['name']}.zip", 'wb') as fd:
                    for chunk in res.iter_content(chunk_size=128):
                        fd.write(chunk)
                with zipfile.ZipFile(f"{temp_dir}/{repo['name']}.zip") as zip_ref:
                    zip_ref.extractall(f"{os.getcwd()}/code/{repo['name']}")


if __name__ == '__main__':
    cli()
