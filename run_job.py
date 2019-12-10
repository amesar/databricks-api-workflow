import sys
import traceback
import logging
from api_workflow_client import ApiWorkflowClient
from args_utils import run_now_parse_args
import utils

def run(url, token, job_id, sleep_seconds, timeout_seconds, params):
    logging.info("url: {}".format(url))
    client = ApiWorkflowClient(url, token, sleep_seconds, timeout_seconds)
    logging.info("job_id: {}".format(job_id))
    logging.info("params: {}".format(params))
    logging.info("timeout_seconds: {}".format(timeout_seconds))

    dct = client.run_now(job_id, params)
    run_id = dct['run_id']
    logging.info("New run_id: {}".format(run_id))
    client.wait_until_run_is_done(run_id)

    dct = client.get_run(run_id)
    if not 'cluster_instance' in dct:
        import json
        jdct = json.dumps(dct,indent=2)
        logging.error("ERROR: response: {}".format(jdct))
        logging.error("ERROR: No 'cluster_instance' in get_run() response for run_id {}".format(run_id))
    else:
        cluster_id = dct['cluster_instance']['cluster_id'] 
        logging.info("cluster_id: {}".format(cluster_id))
        job_status = dct['state']['result_state']
        logging.info("job_status: {}".format(job_status))
        log_dir = dct['cluster_spec']['new_cluster']['cluster_log_conf']['dbfs']['destination'] + '/' + cluster_id
        logging.info("log_dir: {}".format(log_dir))

if __name__ == "__main__":
    try:
        args = run_now_parse_args()
        params = [] if args.job_params is None else args.job_params.split(" ")
        print("params:",params)
        run(args.url, args.token, args.job_id, args.sleep_seconds, args.timeout_seconds, params)
        sys.exit(0)
    except Exception,e:
        traceback.print_exc()
        logging.error("ERROR: {}".format(e))
        sys.exit(1)
