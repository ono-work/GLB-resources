#!/bin/zsh
# Verifier queue (memory-gated via barrier/memgate.py). Waits for each producer certificate before verifying it.
cd ${0:a:h}/..
for f in "$@"; do
  until [ -f harvest/$f.json ]; do sleep 60; done
  echo "=== verify $f $(date)"
  /usr/bin/time -l .venv/bin/python harvest/verify_psi.py harvest/$f.json > harvest/logs/verify_$f.out 2>&1
  echo "exit $? $(date)"; grep -E "AUDIT|real|maximum resident" harvest/logs/verify_$f.out
done
echo VERIFY_QUEUE_DONE
