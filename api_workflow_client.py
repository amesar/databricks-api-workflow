import sys
import os
import time
import json
import logging
from api_client import ApiClient
import utils

logging.info("Python version: {}".format(sys.version))

class ApiWorkflowClient(object):
    """ 
    API Workflow Client. Wrapping some low-level REST endpoints with workflow logic.
    """

    def _default_timeout_func(self):
        raise Exception("Timeout of {} seconds exceeded".format(self.timeout_seconds))
    
    def __init__(self, base_url, token, sleep_seconds=2, timeout_seconds=sys.maxsize, timeout_func=_default_timeout_func, verbose=True):
        """
        :param base_url: Base URL of API such as https://acme.cloud.databricks.com/api/2.0
        :param token: API token
        :param sleep_seconds: Seconds to sleep when polling for cluster readiness
        :param timeout_seconds: Timeout in seconds
        :param verbose: To be verbose or not?
        """
        self.api_client = ApiClient(base_url, token)
        self.base_url = base_url
        self.sleep_seconds = sleep_seconds
        self.timeout_seconds = timeout_seconds
        self.timeout_func = timeout_func
        self.verbose = verbose
        config_file = "config.json"
        if os.path.exists(config_file):
            logging.info("Reading config file {}".format(config_file))
            with open(config_file, 'rb') as f:
                dct = json.loads(f.read())
            self.cluster_noninit_states = set(dct['cluster_noninit_states'])
            self.run_terminal_states = set(dct['run_terminal_states'])
        else:
            self.cluster_noninit_states = { "RUNNING", "TERMINATED", "ERROR", "UNKNOWN" }
            self.run_terminal_states = { "TERMINATED", "SKIPPED", "INTERNAL_ERROR" }
        logging.info("cluster_noninit_states: {}".format(self.cluster_noninit_states))
        logging.info("run_terminal_states: {}".format(self.run_terminal_states))

    def __repr__(self):
        return "[base_url={} sleep_seconds={}]".format(self.base_url, self.sleep_seconds)
    
    
    def _mk_url(self, resource):
        return self.base_url + "/" + resource

    def _check_response(self, rsp):
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise Exception("HTTP status code: " + str(rsp.status_code)+" Reason: "+rsp.reason)

    
    def get_cluster(self, cluster_id):
        """ Get cluster details. """
        return self.api_client.get_cluster(cluster_id)

    def get_cluster_state(self, cluster_id):
        """ Return cluster state for cluster_id. """
        dct = self.api_client.get_cluster(cluster_id)
        logging.info("    cluster_id: {} is in {} state".format(cluster_id, dct["state"]))
        return dct["state"]
    
    def start_cluster(self, cluster_id):
        return self.api_client.start_cluster(cluster_id)
    
    def create_cluster(self, data):
        """ Create a new cluster. """
        return self.api_client.create_cluster(data)
        
    def wait_until_cluster_is_created_for_run(self, run_id):
        """ Wait until cluster_instance for specified run_id is available. """ 
        name = "cluster_is_created_for_run"
        def is_done(run_id):
            dct = self.get_run(run_id)
            res = "cluster_instance" in dct
            if res: 
                cluster_id = dct["cluster_instance"]["cluster_id"]
                msg = "Done waiting for '{}'. Cluster {} has been created for run {}.".format(name,cluster_id,run_id)
            else:
                msg = "Waiting for '{}'. run {}.".format(name,run_id)
            return (res,msg,dct)
        return self._wait_until(is_done,run_id,"Start waiting for '{}'.".format(name))

    def wait_until_cluster_is_running(self, cluster_id):
        """ Wait until cluster state is in RUNNING, TERMINATED, ERROR or UNKNOWN state. """
        name = "until cluster is running"
        def is_done(cluster_id):
            dct = self.get_cluster(cluster_id)
            state = dct["state"]
            res = state in self.cluster_noninit_states
            msg0 = "Cluster {} is in {} state".format(cluster_id, state)
            msg = "Done waiting for '{}'. {}".format(name,msg0) if res else "Waiting for '{}'. {}.".format(name,msg0)
            return (res,msg,dct)
        return self._wait_until(is_done,cluster_id,"Start waiting for '{}'".format(name))

        
    def run_now(self, job_id, jar_params):
        """ Run the job_id with specified jar_params. """
        return self.api_client.run_now(job_id, jar_params)
    
    def run_submit(self, data, parameters=[]):
        """ Run submit with specified parameters. """
        if len(parameters) > 0:
            dct = json.loads(data)
            task = dct.get("spark_jar_task",None)
            if task is not None:
                dct["spark_jar_task"]["parameters"] = parameters
                data = json.dumps(dct)
        return self.api_client.run_submit(data)
    
    def get_run(self, run_id):
        """ Get run details. """
        return self.api_client.get_run(run_id)

    def get_run_state(self, run_id):
        """ Get run state. """
        dct = self.api_client.get_run(run_id)
        return dct["state"]

    def wait_until_run_is_done(self, run_id):
        """ Wait until specified run_id is done, i.e. life_cycle_state is either TERMINATED, SKIPPED, INTERNAL_ERROR. """
        name = "until_run_is_done"
        def is_done(run_id):
            dct = self.get_run_state(run_id)
            res = dct["life_cycle_state"] in self.run_terminal_states
            msg0 = "Run {} is in {} life_cycle_state".format(run_id,dct["life_cycle_state"]) 
            msg = "Done waiting for '{}'. {}.".format(name,msg0) if res else "Waiting for '{}'. {}.".format(name,msg0)
            return (res,msg,dct)
        return self._wait_until(is_done,run_id,"Start waiting for '{}'. Run {}.".format(name,run_id))

    def _capitalize(self, s): return s[0].capitalize() + s[1:]

    def _wait_until(self, funk, obj_id, init_msg):
        idx = 0
        start = time.time()
        if self.verbose: logging.info("{}".format(init_msg))
        while True:
            if time.time()-start > self.timeout_seconds:
                self.timeout_func(self)
            (res,msg,dct) = funk(obj_id)
            time.sleep(self.sleep_seconds)
            if self.verbose: logging.info("{}".format(msg))
            if res: break
            idx += 1
        nsecs = time.time()-start
        logging.info("Processing time: {0:.2f} seconds".format(nsecs))
        return dct
