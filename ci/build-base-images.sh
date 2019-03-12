CHANGED_FILES=$(git diff --name-only $TRAVIS_COMMIT_RANGE)
echo "Changed files: ${CHANGED_FILES}"

