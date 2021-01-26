#!/bin/bash

echo "RUNNING PREBUILD SCRIPTS"
# if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then 
#     ./scripts/helpers/check_commit_subject.sh -r  $TRAVIS_COMMIT_RANGE
# fi

handle_test_result(){
    EXIT_CODE=$1
    RESULT="$2"
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Commit check was succesfull."
        python setup.py test
    else
        echo "Errors in commit message."
    fi
    # Print RESULT if not empty
    if [ -n "$RESULT" ] ; then
        echo "\n$RESULT"
    fi
    # Reset color
    echo "${NO_COLOR}"
}

run_git_check(){
    echo "Running gitlint..."
    RESULT=$(gitlint --commits $GIT_ORIGIN..$GIT_LAST 2>&1)
    local exit_code=$?
    handle_test_result $exit_code "$RESULT"
    return $exit_code
}

pip install gitlint
run_git_check