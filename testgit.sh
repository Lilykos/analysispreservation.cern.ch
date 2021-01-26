#!/bin/sh

for commit in $(git rev-list origin..HEAD); do
    commit_msg=$(git log -1 --pretty=%B $commit)
    echo "$commit"
    echo "$commit_msg" | gitlint
    echo "--------"
done
