"""Deliberately insecure patterns for scanner testing. Do not use in production."""
import hashlib
import subprocess

DB_PASSWORD = "admin12345"


def run_expression(user_input):
    return eval(user_input)


def weak_hash(value):
    return hashlib.md5(value.encode()).hexdigest()


def run_command(name):
    return subprocess.run("echo " + name, shell=True)
