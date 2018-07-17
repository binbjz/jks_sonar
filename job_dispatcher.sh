#!/bin/bash
#filename: job_dispatcher.sh
#
#desc: access sonar by jenkins with manual, crontab, push or pull request to trigger.
#

NOARGS=65
NOMATCH=122
E_CERROR=129

# check parm num
if [ $# -ne 1 ]; then
   echo "Usage: ${BASH_SOURCE[0]} pu|pr"
   exit $NOARGS
fi

# specify config template
configSwitch=$1
puConfigTemplate=puInitConfigTemplate.xml
prConfigTemplate=prInitConfigTemplate.xml

case "$configSwitch" in
"pu")
    # using pu config template
    configTemplate=$puConfigTemplate
    ;;
"pr")
    # using pull request config template
    configTemplate=$prConfigTemplate
    ;;
* )
    echo "Please specify valid config template type"
    exit $NOMATCH
    ;;
esac

# job suffix and cur dir
bashExec=`which bash`
jobSuf="_static-analyze"
curDir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# replace kw with specified parm
replace_kw(){
    sed -re "s#<repo_name>#${1}#g; \
             s#<misid>#${misId}#g; \
             s#(<repositoryName>).*(</repositoryName>)#\1${1}\2#g; \
             s#(<url>).*(</url>)#\1${2}\2#g; \
             s#(sonar.projectKey=).*#\1${3}#g; \
             s#(sonar.projectName=).*#\1${4}#g" \
    $configTemplate > $curDir/$configTemplate.$$
}

# load parm template
source parmTemplate.sh

# perform access action
for job in $jobList;
do
    set -- ${!job}
    replace_kw $1 $2 $3 $4

    # create job with sonar
    jobName=${1}${jobSuf}
    $bashExec ${curDir}/job_handler.sh -c $jobName -f ${curDir}/${configTemplate}.$$ \
    || exit $E_CERROR
    echo

    # just build with pu job
    if [[ "$configSwitch" == "pu" ]]; then
        sleep 2

        # build
        #$bashExec ${curDir}/job_handler.sh -s $jobName

        # build with parameters
        $bashExec ${curDir}/job_handler.sh -s $jobName -p test
    fi

    # cleanup env
    rm -rf ${curDir}/${configTemplate}.$$ &> /dev/null
    echo "op $jobName done.."
    echo
done
