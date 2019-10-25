''' Command line arguments '''

import sys
from argparse import ArgumentParser

def build_base_parser():
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="API URL", required=True)
    parser.add_argument("-t", "--token", dest="token", help="API token", required=True)
    parser.add_argument("-s", "--sleep_seconds", dest="sleep_seconds", help="sleep_seconds", default=5, type=int)
    parser.add_argument("-T", "--timeout_seconds", dest="timeout_seconds", help="timeout_seconds", default=sys.maxsize, type=int)
    parser.add_argument("-p", "--job_params", dest="job_params", help="job_params" )
    return parser

def run_submit_parse_args():
    parser = build_base_parser()
    parser.add_argument("-f", "--json_file", dest="json_file", help="job_id", required=True)
    return parser.parse_args()

def run_now_parse_args():
    parser = build_base_parser()
    parser.add_argument("-j", "--job_id", dest="job_id", help="job_id", required=True, type=int)
    return parser.parse_args()
