#!/bin/zsh
# Producer queue (memory-gated): run_produce_queue.sh ID S C [ID S C ...]
cd ${0:a:h}/..
while [ $# -ge 3 ]; do
  ID=$1; S=$2; C=$3; shift 3
  echo "=== produce $ID $(date)"
  /usr/bin/time -l .venv/bin/python harvest/psi_exact.py "$S" "$C" > harvest/logs/produce_$ID.out 2>&1
  echo "exit $? $(date)"; grep -E "TOTAL|real|maximum resident" harvest/logs/produce_$ID.out
done
echo PRODUCE_QUEUE_DONE
