#!/usr/bin/env bash

if [ $# -ne 2 ]; then
  echo "usage: $0 {serverName} {serverNum}"
  exit 1
fi

serverName=$1
serverNum=$2

confP="supervisord.conf"
nginxP="nginx_tornado.conf"
cp template/nginx.conf ./

confH=""

function catConf() {
  serverNo=`expr 0 + ${1}`

  confH=${confH},tornado-${serverNo}

  echo "    server tornado:${serverNo} max_fails=5 fail_timeout=60s;" >> ${nginxP}

  cat >> ${confP} <<EOF
[program:tornado-${serverNo}]
command=python /project/app/app.py --env=prod --type=${serverName} --name=${serverNo}
directory=/project/app/
user=root
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
;redirect_stderr=true
;stdout_logfile=/var/log/tornado_PyGW.log
;stdout_logfile_maxbytes=500MB
;stdout_logfile_backups=2
;loglevel=info

EOF
}


head -171 template/${confP} > ${confP}
head -1 template/${nginxP} > ${nginxP}

for NO in $(seq 1 ${serverNum})
do
  catConf ${NO}
done

sed -i 172i\; ${confP}
sed -i 172i\programs=${confH:1} ${confP}
tail -89 template/${nginxP} >> ${nginxP}
