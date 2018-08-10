"""
Written by Daniel Sungju Kwon

This is running extra rules to detect known issues.
"""
import os
import sys
import re
import importlib

import crashcolor

modules = []
sysinfo = {}

def get_system_info():
    global sysinfo

    resultlines = exec_crash_command("sys").splitlines()
    for line in resultlines:
        words = line.split(":")
        sysinfo[words[0].strip()] = words[1].strip()


def load_rules():
    global modules
    global sysinfo

    pysearchre = re.compile('.py$', re.IGNORECASE)
    try:
        cmd_path_list = os.environ["PYKDUMPPATH"]
        path_list = cmd_path_list.split(':')
        source_path = ""
        for path in path_list:
            if os.path.exists(path + "/rules"):
                source_path = path + "/rules"
                break
    except:
        print ("Couldn't find ./rules directory")
        return

    rulefiles = filter(pysearchre.search, os.listdir(source_path))
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    rules = map(form_module, rulefiles)
    importlib.import_module('rules')
    for rule in rules:
        if not rule.startswith('.__'):
            new_module = importlib.import_module(rule, package="rules")
            if new_module.add_rule(sysinfo) == True:
               modules.append(new_module)
    return modules


def print_result(result_list):
    for result_dict in result_list:
        print("=" * 75)
        crashcolor.set_color(crashcolor.LIGHTRED)
        if "TITLE" in result_dict:
            print("ISSUE: %s" % result_dict["TITLE"])
        else:
            print("No title given")
        crashcolor.set_color(crashcolor.RESET)
        print("-" * 75)
        if "MSG" in result_dict:
            print(result_dict["MSG"])
        else:
            print("No message given")
        print("-" * 75)

        print("KCS:")
        if "KCS_TITLE" in result_dict:
            print("\t%s" % result_dict["KCS_TITLE"])
        else:
            print("\tNo subject for KCS")
        crashcolor.set_color(crashcolor.BLUE)
        if "KCS_URL" in result_dict:
            print("\t%s" % result_dict["KCS_URL"])
        else:
            print("\tNo URL for KCS")
        crashcolor.set_color(crashcolor.RESET)

        print("Resolution:")
        crashcolor.set_color(crashcolor.RED)
        if "RESOLUTION" in result_dict:
            print("\t%s" % result_dict["RESOLUTION"])
        else:
            print("\tNo resolution given")
        crashcolor.set_color(crashcolor.RESET)
        print("-" * 75)


def run_rules():
    global modules
    global sysinfo

    issue_count = 0

    for module in modules:
        result_list = module.run_rule(sysinfo)
        if result_list != None:
            issue_count = issue_count + len(result_list)
            print_result(result_list)

    if issue_count > 0:
        print("*" * 75)
        crashcolor.set_color(crashcolor.RED | crashcolor.BLINK)
        print("\tWARNING: %d issue%s detected" %
              (issue_count, "s" if issue_count > 1 else ""))
        crashcolor.set_color(crashcolor.RESET)
        print("*" * 75)
    else:
        print("No issues detected")

def autocheck():
    get_system_info()
    load_rules()
    run_rules()


if ( __name__ == '__main__'):
        autocheck()