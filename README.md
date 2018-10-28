# Jenkins controller and Sonar access with grouping


It will control jenkins job and sonar access with grouping.

This project was written in **bash**, **python** and **xml**.



### It _does..._

* Allow you to control **jenkins job** action.
* Allow you to access **sonar by jenkins with pull request to trigger**.
* Get **repos which contains all qcs** and show different time periods repos with **HTML diff style**.
* Configure **user access and hook** for git repository.
* Update **Dx Recipients** for ci job in batches.


----


## Table of Contents

* **[How It Works](#how-it-works)**
* **[How It Generates Repo Template and Compares Different Time Repo](#how-it-generates-repo-template-and-compares-different-time-repo)**
* **[How To Run It For Job Handler](#how-to-run-it-for-job-handler)**
* **[How To Run It For Job Dispatcher](#how-to-run-it-for-job-dispatcher)**
* **[How To Configure user access And Hook](#how-to-configure-user-access-and-hook)**
* **[How To Update Dx Recipients And Sonar Info And Post Notification](#how-to-update-dx-recipients-and-sonar-info-and-post-notification)**


----


## How It Works
* **stash and org** to collect and analyze group mapping.
* **repo handler** to generate temp template, **dispatcher** update **template info**
* according to the specified parameters and then calls **handler** with **repo template** to access.
* prInitConfigTemplate.xml is **pull request** config tmpl - access sonar with pull request to **master**.


----


## How It Generates Repo Template and Compares Different Time Repo

* repo handler allow you to generate repo list which contains qcs all repos.
* repo handler allow you to compare different time periods repos which contains qcs all repos, and generate diff html to show you.

1. **generate repo list and compare different time periods repos**
    ```sh
    $ python repo_handler.py
    ```


----


## How To Run It For Job Handler

* job handler allow you to control jenkins job action.

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

6. **delete job** 
    ```sh
    $ bash job_handler.sh -d <job name>
    ``` 

7. **enable job**
    ```sh
    $ bash job_handler.sh -e <job name>
    ```

8. **disable job**
    ```sh
    $ bash job_handler.sh -k <job name>
    ```
    
9. **check job build result**
    ```sh
    $ bash job_handler.sh -q <job name>
    ```

----


## How To Run It For Job Dispatcher

* Allow you to access sonar by jenkins with pull request to trigger for master or test branch .
* Note: Please update git repository template and update user name and api token in handler.

1. **view usage**
    ```sh
    $ bash job_dispatcher.sh
    ```

2. **access sonar by jenkins with pull request to master to trigger**
    ```sh
    $ bash job_dispatcher.sh prm
    ```


----


## How To Configure User Access And Hook

* configure user with repo permission, configure Stash Webhook and Events to Jenkins.

1. **config user and hook**
    ```sh
    $ bash hook_event.sh
    ```


----


## How To Update Dx Recipients And Sonar Info And Post Notification

* Allow you to configure dx recipient and sonar info dynamically.
* Note: Please update dx recipients list first and run it.

1. **update dx recipients and sonar info**
    ```sh
    $ bash job_update_msg.sh
    ```
