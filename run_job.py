from __future__ import print_function
import sys
import traceback
from api_workflow_client import ApiWorkflowClient
from args_utils import run_now_parse_args
from util import log_print

def run(url, token, job_id, sleep_seconds, timeout_seconds, params):
    log_print("url: {}\n".format(url))
    client = ApiWorkflowClient(url, token, sleep_seconds, timeout_seconds)
    log_print("job_id: {}\n".format(job_id))
    log_print("params: {}\n".format(params))
    log_print("timeout_seconds: {}\n".format(timeout_seconds))

    dct = client.run_now(job_id, params)
    run_id = dct['run_id']
    log_print("New run_id: {}\n".format(run_id))
    client.wait_until_run_is_done(run_id)

    dct = client.get_run(run_id)
    if not 'cluster_instance' in dct:
        import json
        jdct = json.dumps(dct,indent=2)
        log_print("ERROR: response: {}\n".format(jdct))
        log_print("ERROR: No 'cluster_instance' in get_run() response for run_id {}\n".format(run_id))
    else:
        cluster_id = dct['cluster_instance']['cluster_id'] 
        log_print("cluster_id: {}\n".format(cluster_id))
        job_status = dct['state']['result_state']
        log_print("job_status: {}\n".format(job_status))
        log_dir = dct['cluster_spec']['new_cluster']['cluster_log_conf']['dbfs']['destination'] + '/' + cluster_id
        log_print("log_dir: {}\n".format(log_dir))

if __name__ == "__main__":
    try:
        args = run_now_parse_args()
        params = [] if args.job_params is None else args.job_params.split(" ")
        print("params:",params)
        run(args.url, args.token, args.job_id, args.sleep_seconds, args.timeout_seconds, params)
        sys.exit(0)
    except Exception,e:
        traceback.print_exc()
        log_print("ERROR: {}\n".format(e))
        sys.exit(1)
