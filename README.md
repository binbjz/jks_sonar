# Jenkins controller and Sonar access


It will control jenkins job and sonar access.

This project was written in **bash**, **python** and **xml**.



### It _does..._

* Allow you to control **jenkins job** action.
* Allow you to access **sonar by jenkins with manual, crontab or push to trigger**.
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
* **[How To Update Dx Recipients And Sonar Info](#how-to-update-dx-recipients-and-sonar-info)**


----


## How It Works

* **repo handler** to generate repo template, **dispatcher** modify **temp config template**
* according to the specified parameters and then calls **handler** with **repo template** to access.
* puInitConfigTemplate.xml is **push** config tmpl - access sonar with manual, crontab or push.
* prInitConfigTemplate.xml is **pull request** config tmpl - access sonar with pull request to **master**.
* prtInitConfigTemplate.xml is **pull request** config tmpl - access sonar with pull request to **test**.


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

3. **access sonar by jenkins with pull request to master to trigger**
    ```sh
    $ bash job_dispatcher.sh prm
    ```

4. **access sonar by jenkins with pull request to test to trigger**
    ```sh
    $ bash job_dispatcher.sh prt
    ```


----


## How To Configure user access and hook

* configure user with repo permission, configure Stash Webhook and Events to Jenkins.
* It can only be used with valid cookie.

1. **config user and hook**
    ```sh
    $ bash hook_event.sh
    ```


----


## How To Update Dx Recipients And Sonar Info

* Allow you to configure dx recipient and sonar info dynamically.
* Note: Please update dx recipients list first and run it.

1. **update dx recipients and sonar info**
    ```sh
    $ bash job_update_msg.sh
    ```
