#!/usr/bin/python
import getpass
import smtplib
import yaml
import shutil
import argparse


def main(path):
    stat = shutil.disk_usage(path)
    sender = 'webmaster@tincher.de'
    receivers = ['joel.ewig@gmail.com']

    disk_usage = f'Disk Usage of {path}: used: {stat.used / (1024**3)}, free: {stat.free / (1024**3)}'

    message = 'Subject: {disk_usage}\n\n{disk_usage}'

    with open('/config.yml', 'r') as configfile:
        config = yaml.safe_load(configfile)
    server = smtplib.SMTP_SSL('smtp.strato.de', 465)
    server.login(config['mail']['username'], config['mail']['password'])
    server.sendmail(sender, receivers, message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='send mail about disk usage')
    parser.add_argument('path', help='path of usage')
    args = parser.parse_args()

    main(args.path)
