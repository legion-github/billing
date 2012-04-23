#!/bin/sh -eu

if [ -z "${1-}" ]; then
	set *.py
fi

export PYTHONPATH='../lib'

success=0
failure=0

rc=0
for pytest; do
	[ -f "$pytest" ] ||
		continue
	printf '=== Test %s ===\n\n' "$pytest"
	if ! python "$pytest"; then
		failure=$(($failure + 1))
		rc=1
	else
		success=$(($success + 1))
	fi
	printf '\n'
done

cat <<EOF
=====================================================================
Summary: $success success, $failure failures

EOF

exit $rc
