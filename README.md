# apiWorkflowClient

ApiWorkflowClient is an opinionated Python wrapper to execute runs synchronously with the Databricks REST API.

## Overview

[ApiWorkflowClient](api_workflow_client.py):
* Intended for basic workflow tasks - either home-grown or Airflow.
* Launches a run and waits until it is in the TERMINATED state by polling the [jobs/runs/get](https://docs.databricks.com/api/latest/jobs.html#runs-get) endpoint.
* Supports both the [jobs/runs/submit](https://docs.databricks.com/api/latest/jobs.html#runs-submit) and [jobs/run-now](https://docs.databricks.com/api/latest/jobs.html#run-now) REST endpoints.

## jobs/runs/submit 

Files
  * [run_submit.py](run_submit.py) - Sample invocation of apiWorkflowClient.run_job_submit()
  * [run_submit.json](run_submit.json) - sample JSON request file

Synopsis
  * Function: ApiWorkflowClient.run_job_submit().
  * Supports only the `spark_jar_task` task.
  * Inserts command-line arguments into JSON payload as `spark_jar_task.parameters` attribute.
  * Launches a run with the JSON file .
  * Prints run ID.
  * Polls until cluster is created.
  * Prints cluster ID.
  * Polls until run is finished.
  * Prints run status and log directory.

Run
```
url=https://acme.cloud.databricks.com/api/2.0
token=MY_TOKEN
file=runs_submit.json
sleep_seconds=3

python run_submit.py -u $url -t $token -f $file -s $sleep_seconds param1 param2

2019-01-02 23:41:57 Processing time: 4.82 seconds
2019-01-02 23:41:58 cluster_id: 0102-234154-bud180
2019-01-02 23:41:58 Start waiting for 'until_run_is_done'. Run 2374686.
2019-01-02 23:42:00 Waiting for 'until_run_is_done'. Run 2374686 is in PENDING life_cycle_state.
2019-01-02 23:42:03 Waiting for 'until_run_is_done'. Run 2374686 is in PENDING life_cycle_state.
...
2019-01-02 23:43:40 Waiting for 'until_run_is_done'. Run 2374686 is in RUNNING life_cycle_state.
2019-01-02 23:43:42 Waiting for 'until_run_is_done'. Run 2374686 is in TERMINATING life_cycle_state.
2019-01-02 23:43:44 Done waiting for 'until_run_is_done'. Run 2374686 is in TERMINATED life_cycle_state..
2019-01-02 23:43:44 Processing time: 106.56 seconds
2019-01-02 23:43:45 log_dir: dbfs:/andre/logs/jobs/run_submit/0102-234154-bud180
```

## jobs/run-now

Files
  * [run_job.py](run_job.py) - Sample invocation of apiWorkflowClient.run_job_submit()
  * [create_job.json](create_job.json) - Sample JSON create job file request

Synopsis
  * You must first create the job with [create_job.json](create_job.json).
  * Function: ApiWorkflowClient.run_job().
  * Supports only the `jar_params` variant for now.
  * Inserts command-line arguments into JSON payload as `jar_params` attribute.
  * Launches a run for the specified job_id.
  * Prints run ID.
  * Polls until run is finished.
  * Prints run status and log directory

Run

```

url=https://acme.cloud.databricks.com/api/2.0
token=MY_TOKEN
job_id=1812
sleep_seconds=3

python job_run.py $url $token $job_id $sleep_seconds param1 param2

2019-01-03 00:35:58 url: https://demo.cloud.databricks.com/api/2.0
2019-01-03 00:35:58 job_id: 11926
2019-01-03 00:36:00 New run_id: 2374690
2019-01-03 00:36:00 Start waiting for 'until_run_is_done'. Run 2374690.
2019-01-03 00:36:03 Waiting for 'until_run_is_done'. Run 2374690 is in PENDING life_cycle_state.
2019-01-03 00:36:05 Waiting for 'until_run_is_done'. Run 2374690 is in PENDING life_cycle_state.
...
2019-01-03 00:37:48 Waiting for 'until_run_is_done'. Run 2374690 is in RUNNING life_cycle_state.
2019-01-03 00:37:51 Waiting for 'until_run_is_done'. Run 2374690 is in TERMINATING life_cycle_state.
2019-01-03 00:37:55 Done waiting for 'until_run_is_done'. Run 2374690 is in TERMINATED life_cycle_state.
2019-01-03 00:37:55 Processing time: 115.29 seconds
2019-01-03 00:37:56 cluster_id: 0103-003601-ales185
2019-01-03 00:37:56 job_status: SUCCESS
2019-01-03 00:37:56 log_dir: dbfs:/andre/logs/jobs/workflowApiClient_run_now/0103-003601-ales185
```

## Sample JAR

[src/main/scala/org/andre/HelloFelidae.scala](sample_jar/src/main/scala/org/andre/HelloFelidae.scala)

A simple jar is provided for testing. Build the jar and push it to dbfs.

```
cd sample_jar

sbt package

curl -X POST -H "Authorization: Bearer MY_TOKEN" \
  -F contents=@target/scala-2.11/amm-hellofelidae_2.11-0.1-SNAPSHOT.jar \
  -F path=dbfs:/andre/jars/amm-hellofelidae_2.11-0.1-SNAPSHOT.jar \
  -F overwrite=true https://demo.cloud.databricks.com/api/2.0/dbfs/put
```

To test the jar locally:
```
spark-submit --class org.andre.HelloFelidae --master local[2] \
  target/scala-2.11/amm-hellofelidae_2.11-0.1-SNAPSHOT.jar \
  tiger

+---+--------------+
| id|          name|
+---+--------------+
|200|Sumatran tiger|
|201|    Amur tiger|
|202|  Bengal tiger|
+---+--------------+
```
