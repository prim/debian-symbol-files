# encoding: utf8

import requests
import subprocess
from bs4 import BeautifulSoup
import logging

import os, sys
import traceback

paths = [
    "debian-security/pool/main/p/python2.7",
    "debian/pool/main/p/python2.7",
    "debian-security/pool/main/g/glibc",
    "debian/pool/main/g/glibc",
]

urls = [
    "https://mirrors.tuna.tsinghua.edu.cn",
    "http://ftp.debian.org",
    "http://security.debian.org",
    "http://archive.debian.org",
    "http://ftp.jp.debian.org",

    "http://apt.x.netease.com:8660",

    "http://ftp.riken.jp/Linux/debian",
    "https://deb.sipwise.com", # 这个很全 但是比较慢
    ]

deb_files = set()

def init_log():
    logFile = 'log'
    logging.basicConfig(
        filename = logFile,
        filemode = 'a',
        level = logging.DEBUG,
        format = '%(asctime)s - %(levelname)s: %(message)s',
        datefmt = '%m/%d/%Y %I:%M:%S %p'
    )

def init_local_files():
    for name in os.listdir("deb"):
        if name.endswith(".deb"):
            deb_files.add(name)

def main():
    init_log()
    init_local_files()
    for url in urls:
        for path in paths:
            rurl = "%s/%s" % (url, path)
            handle_url(rurl)

def handle_url(url):
    print "handle_url", url
    resp = requests.get(url)
    if resp.status_code != 200:
        print "handle_url", url, resp.status_code
        return
    soup = BeautifulSoup(resp.text, 'html.parser')
    for e in soup.find_all('a'):
        href = e.attrs["href"]
        if not href.endswith(".deb"):
            continue
        if "amd64" not in href:
            continue
        if href.startswith("python2.7-dbg") or href.startswith("libc6-dbg"):
            path = "%s/%s" % (url, href)
            handle_deb_file(href, path)
            # print e, e.__dict__
            # print e.get_text()

def handle_deb_file(name, url):
    if name in deb_files:
        # print "seen", name
        return
    print "begin", name
    filename = "./deb/%s" % name
    down_http_file(url, filename)
    run("dpkg -x %s extract/%s" % (filename, name[:-4]))
    save_symbol_files("extract/%s" % name[:-4])

def get_build_id(path):
    try:
        with open(os.devnull, "w") as null:
            s = subprocess.check_output(["readelf", "-n", path], stderr=null)
    except subprocess.CalledProcessError:
        return
    except Exception:
        traceback.print_exc()
        return
    for line in s.split('\n'):
        if "Build ID" in line:
            return line.split()[-1]

def save_symbol_files(dirname):
    for root, dirs, files in os.walk(dirname):
        for file in files:
            file_path = os.path.join(root, file)
            build_id = get_build_id(file_path)
            if build_id is not None:
                cmd = "cp %s symbols/%s.debug" % (file_path, build_id)
                run(cmd)

def run(cmd):
    logging.info("begin %s", cmd)
    if os.system(cmd) != 0:
        logging.info("exit %s", cmd)
        sys.exit(0)
    logging.info("end %s", cmd)

def down_http_file(url, filename):
    resp = requests.get(url, allow_redirects=True)
    with open(filename, "w+") as wf:
        wf.write(resp.content)

main()
