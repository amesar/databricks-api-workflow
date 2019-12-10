import sys
import json
import requests
import logging
import utils

class ApiClient(object):
    """ 
    API Client. Python wrapper for selected Databricks REST API endpoints.
    """

    def __init__(self, base_url, token):
        """
        :param base_url: Base URL of API such as https://acme.cloud.databricks.com/api/2.0
        :param token: API token
        """
        self.base_url = base_url
        self.token = token
        logging.info("base_url: {}".format(base_url))

    def _mk_url(self, resource):
        return self.base_url + "/" + resource

    def _check_response(self, rsp, url):
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise Exception("HTTP status code: {}. Reason: {}. URL: {}".format(str(rsp.status_code),rsp.reason,url))

    def get(self, resource):
        """ Executes an HTTP GET call
        :param resource: Relative path name of resource such as jobs/get?job_id=1776.
        """
        url = self._mk_url(resource)
        rsp = requests.get(url, headers= {'Authorization': 'Bearer '+self.token})
        if rsp.status_code == 404:
            return None
        self._check_response(rsp, url)
        #logging.info("GET: {}".format(rsp.text))
        return json.loads(rsp.text)

    def post(self, resource, data):
        """
        Executes an HTTP POST call
        :param resource: Relative path name of resource such as jobs/runs/submit.
        :param data: JSON request payload.
        """
        url = self._mk_url(resource)
        rsp = requests.post(url, headers= {'Authorization': 'Bearer '+self.token}, data=data)
        self._check_response(rsp,url)
        return json.loads(rsp.text)


    def get_cluster(self, cluster_id):
        """ Get cluster details. """
        return self.get("clusters/get?cluster_id="+cluster_id)
    
    def start_cluster(self, cluster_id):
        """ Start the cluster_id. """
        return self.post("clusters/start", json.dumps(dict(cluster_id=cluster_id)))
    
    def create_cluster(self, data):
        """ Create a new cluster. """
        return self.post("clusters/create", data)
        
    def create_job(self, data):
         """ Create a job with accompanying data. """
         return self.post("jobs/create", data)
    
    def get_job(self, job_id):
        """ Get job details. """
        return self.get("jobs/get?job_id="+str(job_id))
        
    def run_now(self, job_id, jar_params):
        """ Run the job_id with specified jar_params. """
        data = dict(job_id=job_id, jar_params=jar_params)
        return self.post("jobs/run-now", json.dumps(data))
    
    def run_submit(self, data):
        """ Run submit with specified data. """
        return self.post("jobs/runs/submit", data)
    
    def get_run(self, run_id):
        """ Get run details. """
        return self.get("jobs/runs/get?run_id="+str(run_id))
