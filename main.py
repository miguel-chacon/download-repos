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
    items_per_page = 500
    r = requests.get(f"https://api.github.com/orgs/{org}/repos?per_page={items_per_page}", headers=headers)

    if not os.path.exists(f"{os.getcwd()}/code"):
        os.mkdir(f"{os.getcwd()}/code")

    print(f"Total number of repositories: {len(r.json())}\n---------------------------------")

    with tempfile.TemporaryDirectory() as temp_dir:
        for repo in r.json():
            for branch in ['production', 'main', 'master']:
                url = f"https://api.github.com/repos/{org}/{repo['name']}/zipball/{branch}"
                res = requests.get(url, headers=headers, stream=True)
                if res.status_code == 404:
                    continue
                else:
                    print(f"Downloaded -> repo: {repo['name']} - {branch}")
                    with open(f"{temp_dir}/{repo['name']}.zip", 'wb') as fd:
                        for chunk in res.iter_content(chunk_size=1024*1204*10):
                            fd.write(chunk)
                    with zipfile.ZipFile(f"{temp_dir}/{repo['name']}.zip") as zip_ref:
                        zip_ref.extractall(f"{os.getcwd()}/code/")
                    break
                print(f"Error downloading {repo['name']}")


if __name__ == '__main__':
    cli()
