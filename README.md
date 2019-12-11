# ApiWorkflowClient

The ApiWorkflowClient is a semi-opinionated Python wrapper around the Databricks REST API to execute job runs in a synchronous polling manner.

## Overview

* Intended for basic workflow tasks.
* Launches a run and waits until it is finished (TERMINATED state) by polling the [jobs/runs/get](https://docs.databricks.com/api/latest/jobs.html#runs-get) REST endpoint.
* Supports both the [jobs/runs/submit](https://docs.databricks.com/api/latest/jobs.html#runs-submit) and [jobs/run-now](https://docs.databricks.com/api/latest/jobs.html#run-now) endpoints.
* Only supports jar tasks but easy to extend to other tasks.
  * Example job is a [Scala jar](sample_jar).
* [ApiWorkflowClient](api_workflow_client.py) - main workhorse class.
* Requires Python 3.
* Make sure to run python with the `-u` option for unbuffered output so print statements are displayed in real-time.

## jobs/runs/submit 

**Files**
  * [run_submit.py](run_submit.py) - Sample invocation of [ApiWorkflowClient.run_submit](api_workflow_client.py#L105).
  * [run_submit.json](run_submit.json) - Sample JSON request file.

**Synopsis**
  * Databricks documentation - [jobs/runs/submit](https://docs.databricks.com/api/latest/jobs.html#runs-submit).
  * Only supports the `spark_jar_task` task.
  * Inserts command-line arguments into the JSON payload as `spark_jar_task.parameters` attribute.
  * Launches a run based upon the JSON spec file .
  * Prints run ID.
  * Polls until cluster is created.
  * Prints cluster ID.
  * Polls until run is finished.
  * Prints run status and log directory.

**Run**
```
python -u run_submit.py \
  --url https://acme.cloud.databricks.com/api/2.0 \
  --token MY_TOKEN --json_file runs_submit.json --sleep_seconds 3 \
  param1 param2
```

```
2019-12-10 14:52:46 New run_id: 2392940
2019-12-10 14:52:46 Start waiting for 'cluster_is_created_for_run'.
2019-12-10 14:52:48 Waiting for 'cluster_is_created_for_run'. run 2392940.
2019-12-10 14:52:51 Done waiting for 'cluster_is_created_for_run'. Cluster 1210-195246-joyed285 has been created for run 2392940.
2019-12-10 14:52:51 Processing time: 4.68 seconds
2019-12-10 14:52:51 cluster_id: 1210-195246-joyed285
2019-12-10 14:52:51 Start waiting for 'until_run_is_done'. Run 2392940.
2019-12-10 14:52:53 Waiting for 'until_run_is_done'. Run 2392940 is in PENDING life_cycle_state.
2019-12-10 14:52:56 Waiting for 'until_run_is_done'. Run 2392940 is in PENDING life_cycle_state.
. . .
2019-12-10 14:53:55 Waiting for 'until_run_is_done'. Run 2392940 is in RUNNING life_cycle_state.
2019-12-10 14:53:58 Done waiting for 'until_run_is_done'. Run 2392940 is in TERMINATED life_cycle_state.
2019-12-10 14:53:58 Processing time: 66.83 seconds
2019-12-10 14:53:58 log_dir: dbfs:/andre/logs/jobs/run_submit/1210-195246-joyed285
```

## jobs/run-now

**Files**
  * [run_job.py](run_job.py) - Sample invocation of [ApiWorkflowClient.run_now](api_workflow_client.py#L101).
  * [create_job.json](create_job.json) - Sample JSON create job file request

**Synopsis**
  * Databricks documentation - [jobs/run-now](https://docs.databricks.com/api/latest/jobs.html#run-now).
  * You must first create the job with [create_job.json](create_job.json) or through the UI.
  * Only supports the `jar_params` task.
  * Inserts command-line arguments into the JSON payload as `jar_params` attribute.
  * Launches a run for the specified job_id.
  * Prints run ID.
  * Polls until run is finished.
  * Prints run status and log directory

**Run**

```
python -u run_job.py \
  --url https://acme.cloud.databricks.com/api/2.0 \
  --token MY_TOKEN --job_id 1812 --sleep_seconds 3 \
  param1 param2

2019-01-03 00:35:58 url: https://demo.cloud.databricks.com/api/2.0
2019-01-03 00:35:58 job_id: 11926
2019-01-03 00:36:00 New run_id: 2374690
2019-01-03 00:36:00 Start waiting for 'until_run_is_done'. Run 2374690.
2019-01-03 00:36:03 Waiting for 'until_run_is_done'. Run 2374690 is in PENDING life_cycle_state.
2019-01-03 00:36:05 Waiting for 'until_run_is_done'. Run 2374690 is in PENDING life_cycle_state.
. . .
2019-01-03 00:37:48 Waiting for 'until_run_is_done'. Run 2374690 is in RUNNING life_cycle_state.
2019-01-03 00:37:51 Waiting for 'until_run_is_done'. Run 2374690 is in TERMINATING life_cycle_state.
2019-01-03 00:37:55 Done waiting for 'until_run_is_done'. Run 2374690 is in TERMINATED life_cycle_state.
2019-01-03 00:37:55 Processing time: 115.29 seconds
2019-01-03 00:37:56 cluster_id: 0103-003601-ales185
2019-01-03 00:37:56 job_status: SUCCESS
2019-01-03 00:37:56 log_dir: dbfs:/andre/logs/jobs/workflowApiClient_run_now/0103-003601-ales185
```

## Sample JAR

A simple jar is provided for testing. Build the jar and push it to dbfs.
See [sample_jar](sample_jar) and [HelloFelidae.scala](sample_jar/src/main/scala/org/andre/HelloFelidae.scala).

```
cd sample_jar

sbt package

databricks fs cp \
  target/scala-2.11/amm-hellofelidae_2.11-0.1-SNAPSHOT.jar \
  dbfs:/andre/jars \
  --overwrite
```

To test the jar locally.
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
