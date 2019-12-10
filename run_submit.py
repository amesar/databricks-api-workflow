import sys
import json
import traceback
import logging
from api_workflow_client import ApiWorkflowClient
from args_utils import run_submit_parse_args
import utils

def run(url,token,request_file,sleep_seconds,params):
    logging.info("URL: {}".format(url))
    client = ApiWorkflowClient(url,token,sleep_seconds)

    # Read JSON request file
    logging.info("params: {}".format(params))
    with open(request_file,'r') as f:
        data = f.read()

    # Launch run jobs/submit
    dct = client.run_submit(data,params)
    run_id = dct['run_id']
    logging.info("New run_id: {}".format(run_id))

    # Wait until cluster is created
    client.wait_until_cluster_is_created_for_run(run_id)

    # Get cluster ID
    dct = client.get_run(run_id)
    cluster_state = dct['cluster_instance']['cluster_id']
    cluster_id = dct['cluster_instance']['cluster_id']
    logging.info("cluster_id: {}".format(cluster_id))

    # Wait until run is done
    client.wait_until_run_is_done(run_id)

    # Get run status
    dct = client.get_run(run_id)

    # Get cluster log directory
    try:
        log_dir = dct['cluster_spec']['new_cluster']['cluster_log_conf']['dbfs']['destination'] + '/' + cluster_id
        logging.info("log_dir: {}".format(log_dir))
    except KeyError as e:
        pass

if __name__ == "__main__":
    try:
        args = run_submit_parse_args()
        params = [] if args.job_params is None else args.job_params.split(" ")
        print("params:",params)
        run(args.url, args.token, args.json_file, args.sleep_seconds, params)
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        logging.error("ERROR: {}".format(e))
        sys.exit(1)
