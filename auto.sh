#!/bin/bash
# ps control
cd /home/gui/ftp
echo "check thread"
PIDc=`ps aux | grep ftp.py | grep -v grep | awk '{print $2}' | wc -l`
if [ $PIDc -eq 0 ]
then
  echo "thread not exist,open thread"
  python ftp.py
  sleep 1
else
  echo "thread exist"
  sleep 1
fi


