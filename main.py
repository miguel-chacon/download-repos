import sys
import tempfile
import zipfile
import os
import shutil
import re

import requests
import click


def download(url, headers, org, dest):
    files = []

    r = requests.get(url, headers=headers)

    for repo in r.json():
        for branch in ['production', 'test', 'main', 'master']:
            url = f"https://api.github.com/repos/{org}/{repo['name']}/zipball/{branch}"
            res = requests.get(url, headers=headers, stream=True)
            if res.status_code == 404:
                continue
            else:
                files.append(repo['name'])
                with open(f"{dest}/{repo['name']}.zip", 'wb') as fd:
                    for chunk in res.iter_content(chunk_size=1024 * 1204 * 10):
                        fd.write(chunk)
                print(f"Downloaded -> repo: {repo['name']} - {branch}")
                break
            print(f"Error downloading {repo['name']} - {url}")

    link = ''

    try:
        links = r.headers['link'].split(',')
        for i in links:
            if 'rel="next"' in i:
                link = re.search(r'<(\S+)>', i).group(1)
    except KeyError:
        pass

    return files, link


def copy(origin, files):
    for f in files:
        shutil.copyfile(f"{origin}/{f}.zip", f"{os.getcwd()}/code/{f}.zip")


def uncompress(origin, files):
    for f in files:
        with zipfile.ZipFile(f"{origin}/{f}.zip") as zip_ref:
            zip_ref.extractall(f"{os.getcwd()}/code/")


@click.command()
@click.argument('token')
@click.option('--org', default='idoven', show_default=True)
@click.option('--zipped', default='no', show_default=True)
def cli(token, org, zipped):
    headers = {'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28',
               'Authorization': f"Bearer {token}"}

    url = f"https://api.github.com/orgs/{org}/repos?per_page=10"

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(r.json()['message'])
        sys.exit(0)

    if not os.path.exists(f"{os.getcwd()}/code"):
        os.mkdir(f"{os.getcwd()}/code")

    total = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        while True:
            names, url = download(url, headers, org, temp_dir)
            if zipped == 'no':
                uncompress(temp_dir, names)
            else:
                copy(temp_dir, names)

            total += len(names)

            if url == '':
                break

    print(f"--------------------------------\nTotal number of repositories: {total}\n--------------------------------")


if __name__ == '__main__':
    cli()
