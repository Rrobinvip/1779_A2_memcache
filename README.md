# ECE 1779 MEMCACHE - A File caching system simulates AWS auto scaling

## To run
Script must be executed with current shell with intergrated mode. In most cases, Ubuntu use BASH, and macOS use ZSH.
`<shell> -i start.sh`

To find out your shell with `echo $SHELL`.

## To create environment:
1. Create the environment from the `environment.yml` with `conda env create -f environment.yml`
1. Activate the new environment with `conda activate <name_env>`, in this case, the `<name_env>` is `MEMCACHE`
3. Inspect packages with `conda list`

Nodes will run this flask instance to storage picture. [Node server](https://github.com/Rrobinvip/1779_A2_NodeServer)

## General requirements
1. do not consider node failures, no need to be fault tolerant

## Manager app
1. controls the size of the memcache pool
2. Use charts to show the number of nodes as well as to aggregate statistics for the memcache pool including miss rate, hit rate, number of items in cache, total size of items in cache, number of requests served per minute. The charts should display data for the last 30 minutes at 1-minute granularity.
3. Configure the capacity and replacement policy used by memcache nodes. All memcache nodes in the pool will operate with the same configuration.
4. Selecting between two mutually-exclusive options for resizing the memcache pool, defined under this section. 
5. Deleting all application data: A button to delete image data stored in RDS as well as all image files stored in S3, and clear the content of all memcache nodes in the pool (see next section on clearing memachce data).
6. Clearing memcache data: A button to clear the content of all memcache nodes in the pool.

### mutually-exclusive options
1. Max Miss Rate threshold (average for all nodes in the pool over the past 1 minute) for growing the pool.
2. Min Miss Rate threshold (average for all nodes in the pool over the past 1 minute) for shrinking the pool.
3. Ratio by which to expand the pool (e.g., expand ratio of 2.0, doubles the number of memcache nodes).
4. Ratio by which to shrink the pool (e.g., shrink ratio of 0.5, shuts down 50% of the current memcache nodes).

## scaler app
1. automatically resizes the memcache pool based on configuration values set by the manager-app. It should monitor the miss rate of the mecache pool by getting this information using the AWS CloudWatch API. 
2. There should be no need to manually restart the auto-scaler every time the policy is changed.
3. Check for the cache miss rate every one minute.
4. Do NOT use the AWS Auto Scaling feature for this assignment.
5. Limit the maximum size of the memcache node pool set by auto-scaler to 8 and the minimum to 1. 

## frontend 
1. Remove functionality to configure memcache settings.
2. Remove functionality that displays memcache statistics.
3. All image files should be stored in S3.
4. The mapping between keys and image files should be stored in AWS RDS. Do not store the images themselves in the RDS database. It is advised that you use the smallest possible instance of RDS to save on credit. **Important: RDS is an expensive service that can cost several dollars per day for larger instances. To ensure that you do not run out of credits, use one of the smaller instance types (e.g., burstable db.t2.small class) and remember to stop your RDS instance when you are not actively using it.**
5. Route requests to the memcache pool using a consistent hashing approach based on MD5 hashes. For simplicity, assume that the key space is partitioned into 16 equal-size regions which are then allocated to the pool of memcache nodes. Figures 1-3 illustrate how this assignment changes as the pool size changes from one node to two nodes, to three nodes. More information is provided in the Consistent Hashing section below.
6. Add a feature to the front-end that allows the front-end to be automatically notified when the size of the memcache pool changes. In response, the front-end should rebalance the mapping of key regions to nodes, and use the new allocation to route requests to the memcache, or send requests to the manager-app who takes care of the mapping and routing (the design specifications are up to you).

## backend
1. Store memcache statistic every 5 seconds using CloudWatch Custom MetricsLinks to an external site. instead of the database as was done in A1. Also, look at boto3 documentationLinks to an external site. on how to publish these metrics.
