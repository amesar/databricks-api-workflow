import sys
import json
import traceback
from api_workflow_client import ApiWorkflowClient
from args_utils import run_submit_parse_args
from util import log_print

def run(url,token,request_file,sleep_seconds,params):
    log_print("URL: {}\n".format(url))
    client = ApiWorkflowClient(url,token,sleep_seconds)

    # Read JSON request file
    log_print("params: {}\n".format(params))
    with open(request_file,'r') as f:
        data = f.read()

    # Launch run jobs/submit
    dct = client.run_submit(data,params)
    #log_print("run_submit.response:\n {}\n".format(dct))
    run_id = dct['run_id']
    log_print("New run_id: {}\n".format(run_id))

    # Wait until cluster is created
    client.wait_until_cluster_is_created_for_run(run_id)

    # Get cluster ID
    dct = client.get_run(run_id)
    #log_print("get_run.response.1:\n {}\n".format(json.dumps(dct, indent=2)))
    cluster_state = dct['cluster_instance']['cluster_id']
    cluster_id = dct['cluster_instance']['cluster_id']
    log_print("cluster_id: {}\n".format(cluster_id))

    # Wait until run is done
    client.wait_until_run_is_done(run_id)

    # Get run status
    dct = client.get_run(run_id)
    #log_print("get_run.response.2:\n {}\n".format(json.dumps(dct, indent=2)))

    # Get cluster log directory
    log_dir = dct['cluster_spec']['new_cluster']['cluster_log_conf']['dbfs']['destination'] + '/' + cluster_id
    log_print("log_dir: {}\n".format(log_dir))

if __name__ == "__main__":
    try:
        args = run_submit_parse_args()
        params = [] if args.job_params is None else args.job_params.split(" ")
        print("params:",params)
        run(args.url, args.token, args.json_file, args.sleep_seconds, params)
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        log_print("ERROR: {}\n".format(e))
        sys.exit(1)
