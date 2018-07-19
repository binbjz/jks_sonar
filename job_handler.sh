#!/bin/bash
#filename: job_handler.sh
#
#desc: control job with specified action
#

ARGS=2
E_NORMAL=0
E_ARGERROR=56
E_NONFLAG=75
E_NOJOB=126
E_NOCONF=128
userName=<misid>
apiToken=<jenkins api token>
viewName=<jenkins view name>
jenkinsUrl=http://ci.sankuai.com/job/qcs/job/Sonar/view

#======
#jobName=qcs.settle.c.account_static-analyze
#configFile=configTemplate.xml
#viewName=结算组
#======

echo_(){
    if [ $# -ne "$ARGS" ]; then
        echo "Usage: $FUNCNAME (g|r) OutputString"
        exit $E_ARGERROR
    fi

    case "$1" in
      g) echo -e "\033[2;36m$2\033[0m" ;;
      r) echo -e "\033[2;31m$2\033[0m" ;;
      n) echo ;;
      *) echo "Please specify option \"g\" or \"r\"" ;;
    esac
}

help_info(){
    echo_ g "Usage: `basename $0` options (-h) print help information"
    echo_ g "       `basename $0` options (-c) create jenkins job with specify jobName."
    echo_ g "       `basename $0` options (-u) update jenkins job with specify jobName."
    echo_ g "       `basename $0` options (-f) create jenkins job with specify config template."
    echo_ g "       `basename $0` options (-d ) delete jenkins job with specify jobName."
    echo_ g "       `basename $0` options (-r ) receive jenkins config with specify jobName."
    echo_ g "       `basename $0` options (-s ) start jenkins job with specify jobName."
    echo_ g "       `basename $0` options (-p ) start jenkins job with specify jobName and parm."
    echo_ g "       `basename $0` options (-e ) enable jenkins job with specify jobName."
    echo_ g "       `basename $0` options (-k ) disable jenkins job with specify jobName."
    echo_ n ""
    echo_ g "Example: `basename $0` (-c|-u) jobName -f config.xml | -s jobName | -s jobName -p jobParm | -d jobName | -r jobName | -e jobName | -k jobName"
}

create_job(){
    echo_ g "creating job -- ${1} with ${2##/*/}"
    curl -s -u ${userName}:${apiToken} -X POST "${jenkinsUrl}/${viewName}/createItem?name=${1}" --data-binary "@${2}" -H "Content-Type: text/xml"
}

update_job(){
    echo_ g "updating job -- $1 with ${2##/*/}"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/config.xml --data-binary "@${2}" -H "Content-Type: text/xml"
}

delete_job(){
    echo_ g "deleting job -- $1"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/doDelete
}

start_job(){
    echo_ g "starting job -- $1"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/build
}

start_job_with_parm(){
    # Note: if your job with string parm "branch", so you can use it.
    echo_ g "starting job -- $1"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/buildWithParameters?branch=$2
}

receive_job(){
    echo_ g "receiving job -- ${1}"
    curl -s -u ${userName}:${apiToken} -X GET ${jenkinsUrl}/${viewName}/job/${1}/config.xml -o ${1}_config.xml
}

enable_job(){
    echo_ g "enabling job -- ${1}"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/enable
}

disable_job(){
    echo_ g "disabling job -- ${1}"
    curl -s -u ${userName}:${apiToken} -X POST ${jenkinsUrl}/${viewName}/job/${1}/disable
}

while getopts :c:u:s:p:f:d:r:e:k:h options
do
    case $options in
      c)
          oFlag=1
          cOPTARG="$OPTARG";;
      u)
          oFlag=10
          cOPTARG="$OPTARG";;
      f)
          fFlag=6
          fOPTARG="$OPTARG";;
      d)
          oFlag=2
          cOPTARG="$OPTARG";;
      r)
          oFlag=3
          cOPTARG="$OPTARG";;
      s)
          oFlag=5
          cOPTARG="$OPTARG";;
      p)
          oFlag=4
          pOPTARG="$OPTARG";;
      e)
          oFlag=7
          cOPTARG="$OPTARG";;
      k)
          oFlag=8
          cOPTARG="$OPTARG";;
      h)
          oFlag=9;;
     \?)
          echo_ r "Unknow option $OPTARG";;
      :)
          echo_ r "No parameter value for option $OPTARG";;
      *)
          echo_ r "Unknow error while processing options";;
    esac
done

# job name and config file will be specified. 
jobN=${cOPTARG}
configTemplate=${fOPTARG}

check_jobname(){
    if [[ -z ${jobN} ]]; then 
        echo_ r "** Please specify job name."
        exit $E_NOJOB
    fi
}

check_config(){
    if [[ ! -e "${configTemplate}" ]]; then
        echo_ r "** Please specify valid config Template."
        exit $E_NOCONF
    fi
}

# start job with parm
jobParm=${pOPTARG}


if [[ "$oFlag" -eq 1 && "$fFlag" -eq 6 ]]; then
    check_config
    create_job $jobN $configTemplate
elif [[ "$oFlag" -eq 10 && "$fFlag" -eq 6 ]]; then
    check_config
    update_job $jobN $configTemplate
elif [[ "$oFlag" -eq 2 ]]; then
    delete_job $jobN 
elif [[ "$oFlag" -eq 3 ]]; then
    receive_job $jobN
elif [[ "$oFlag" -eq 4 ]]; then
    check_jobname
    start_job_with_parm $jobN $jobParm
elif [[ "$oFlag" -eq 5 ]]; then
    start_job $jobN
elif [[ "$oFlag" -eq 7 ]]; then
    enable_job $jobN
elif [[ "$oFlag" -eq 8 ]]; then
    disable_job $jobN
elif [[ "$oFlag" -eq 9 ]]; then
    help_info 
else
    echo_ g "Use -h for help"
    exit "$E_NONFLAG"
fi

exit "$E_NORMAL"
