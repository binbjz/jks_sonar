# Jenkins controller and Sonar access


It will control jenkins job and sonar access.

This project was written in **bash**, **python** and config template.



### It _does..._

* Allow you to control **jenkins job**.
* Allow you to access **sonar by jenkins with manual, crontab or push to trigger**.
* Allow you to access **sonar by jenkins with pull request to trigger**.
* Get repos which contains all qcs.
* Show different time periods repos with HTML style.


----


## Table of Contents

* **[How It Works](#how-it-works)**
* **[How It Generates Repo Template](#how-it-generates-repo-template)**
* **[How It Compares Different Time Repo](#how-it-compares-different-time-repo)**
* **[How To Run It For Job Handler](#how-to-run-it-for-job-handler)**
* **[How To Run It For Job Dispatcher](#how-to-run-it-for-job-dispatcher)**
* **[Show Repo Diff](#show-repo-diff)**


----


## How It Works

* **repo handler** to generate repo template, **dispatcher** modify **temp config template**
* according to the specified parameters and then calls **handler** with **repo template** to access.
* puInitConfigTemplate.xml is pu config tmpl - access sonar with manual, crontab or push.
* prInitConfigTemplate.xml is pr config tmpl - access sonar with pull request.


----


## How It Generates Repo Template

* repo handler allow you to generate repo list which contains qcs all repos.

1. **generate repo list**
    ```sh
    $ python repo_handler.py
    ```


----


## How It Compares Different Time Repo

* repo diff allow you to compare different time periods repos which contains qcs all repos,
* and generate diff html to show you.

1. **compare different time periods repos**
    ```sh
    $ python repo_diff.py
    ```


----


## How To Run It For Job Handler

* job handler allow you to control jenkins job.

1. **view usage**
    ```sh
    $ bash job_handler.sh
    $ bash job_handler.sh -h
    ```

2. **create job with config template**
    ```sh
    $ bash job_handler.sh -c <job name> -f <config.xml>
    ```

3. **update job with config template**
    ```sh
    $ bash job_handler.sh -u <job name> -f <config.xml>
    ```

4. **run job**
    ```sh
    $ bash job_handler.sh -s <job name>
    ```

5. **run job with parameter**
    ```sh
    $ bash job_handler.sh -s <job name> -p <parameter value>
    ```

6. **delete job** ```sh $ bash job_handler.sh -d <job name> ``` 7. **enable job** ```sh $ bash job_handler.sh -e <job name> ```

8. **disable job**
    ```sh
    $ bash job_handler.sh -k <job name>
    ```


----


## How To Run It For Job Dispatcher

* Allow you to access sonar by jenkins with manual, crontab or push to trigger.
* Allow you to access sonar by jenkins with pull request to trigger.
* Allow you to generate repo template by using repo handler.
* Note: Please update git repository template and update user name and api token in handler.

1. **view usage**
    ```sh
    $ bash job_dispatcher.sh
    ```

2. **access sonar by jenkins with manual, crontab or push to trigger**
    ```sh
    $ bash job_dispatcher.sh pu
    ```

3. **access sonar by jenkins with pull request to trigger**
    ```sh
    $ bash job_dispatcher.sh pr
    ```



----


## Show Repo Diff

* [repo diff](http://git.sankuai.com/v1/bj/projects/~ZHAOBIN11/repos/jenkins-sonar/browse/repoDiff.html?at=master&auto=false "repo diff")
