# Jenkins controller and Sonar access


It will control jenkins job and sonar access.

This project was written in **bash** and config template.



### It _does..._

* Allow you to control **jenkins job**.
* Allow you to access **sonar with jenkins**.
* Allow you to access **sonar with pull request to trigger**.


----


## Table of Contents

* **[How It Works](#how-it-works)**
* **[How To Run It For Job Handler](#how-to-run-it-for-job-handler)**
* **[How To Run It For Job Dispatcher](#how-to-run-it-for-job-dispatcher)**


----


## How It Works

* **dispatcher** modify **temp config template** according to the specified parameters and then calls **handler** to access.
* accessInitConfigTemplate.xml is basic cofig template for access sonar with crontab.
* prInitConfigTemplate.xml is pr config template for access sonar with pull request to trigger.


----


## How To Run It For Job Handler

* job handler allow you to control jenkins job.

1. **view usage**    
    ```sh
    $ bash job_handler.sh
    $ bash job_handler.sh -h
    ```

2. **creating job with config template**
    ```sh
    $ bash job_handler.sh -c <job name> -f <config.xml>
    ```

3. **updating job with config template**
    ```sh
    $ bash job_handler.sh -u <job name> -f <config.xml>
    ```

4. **running job**
    ```sh
    $ bash job_handler.sh -s <job name>
    ```

5. **running job with parameter**
    ```sh
    $ bash job_handler.sh -s <job name> -p <parameter value>
    ```

6. **deleting job**
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

* Job Dispatcher allow you to access sonar with jenkins.
* Job Dispatcher allow you to access sonar with pull request to trigger.
* Note: Please modify job parameter and job list with your configuration.

1. **view usage**
    ```sh
    $ bash job_dispatcher.sh
    ```
   
2. **access sonar with jenkins**
    ```sh
    $ bash job_dispatcher.sh accs
    ```

3. **access sonar with pull request to trigger**
    ```sh
    $ bash job_dispatcher.sh pr
    ```

