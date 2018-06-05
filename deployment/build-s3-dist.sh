#!/bin/bash

# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#sudo yum-config-manager --enable epel
#sudo yum update -y
#sudo pip install --upgrade pip
#alias sudo='sudo env PATH=$PATH'
#sudo  pip install --upgrade setuptools
#sudo pip install --upgrade virtualenv

# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh source-bucket-base-name version
# source-bucket-base-name should be the base name for the S3 bucket location where the template will source the Lambda code from.
# The template will append '-[region_name]' to this bucket name.
# For example: ./build-s3-dist.sh solutions
# The template will then expect the source code to be located in the solutions-[region_name] bucket

# Check to see if input has been provided:
if [ $# -ne 2 ]; then
    echo "Please provide two arguments: 1) the base source bucket name where the lambda code will eventually reside and 2) the version number.\nFor example: ./build-s3-dist.sh solutions v1.0"
    exit 1
fi

# Build source
echo "Staring to build distribution"
echo "export deployment_dir=`pwd`"
export deployment_dir=`pwd`
echo "mkdir -p dist"
mkdir -p dist
echo "cp -f server-fleet-management-at-scale.yaml dist/server-fleet-management-at-scale.template"
cp -f server-fleet-management-at-scale.yaml dist/server-fleet-management-at-scale.template
echo "cp -f server-fleet-management-at-scale-inspector.yaml dist/server-fleet-management-at-scale-inspector.template"
cp -f server-fleet-management-at-scale-inspector.yaml dist/server-fleet-management-at-scale-inspector.template
echo "Updating code source bucket in templates with $1"
replace="s/%%BUCKET_NAME%%/$1/g"
echo "sed -i '' -e $replace dist/server-fleet-management-at-scale.template"
sed -i '' -e $replace dist/server-fleet-management-at-scale.template
echo "sed -i '' -e $replace dist/server-fleet-management-at-scale-inspector.template"
sed -i '' -e $replace dist/server-fleet-management-at-scale-inspector.template
echo "Updating version in templates with $2"
replace="s/%%VERSION%%/$2/g"
echo "sed -i '' -e $replace dist/server-fleet-management-at-scale.template"
sed -i '' -e $replace dist/server-fleet-management-at-scale.template
echo "sed -i '' -e $replace dist/server-fleet-management-at-scale-inspector.template"
sed -i '' -e $replace dist/server-fleet-management-at-scale-inspector.template

pwd
echo "Four Lambda functions to package"
echo "cp ../source/*.py dist"
cp ../source/*.py dist
cd dist
echo "zip sfm-resource-data-sync.zip sfm-resource-data-sync.py"
zip sfm-resource-data-sync.zip sfm-resource-data-sync.py
echo "zip sfm-respond-to-inspector-agent-id-findings.zip sfm-respond-to-inspector-agent-id-findings.py"
zip sfm-respond-to-inspector-agent-id-findings.zip sfm-respond-to-inspector-agent-id-findings.py
echo "zip sfm-respond-to-inspector-assessment-complete.zip sfm-respond-to-inspector-assessment-complete.py"
zip sfm-respond-to-inspector-assessment-complete.zip sfm-respond-to-inspector-assessment-complete.py
echo "zip sfm-subscribe-inspector-event.zip sfm-subscribe-inspector-event.py"
zip sfm-subscribe-inspector-to-event.zip sfm-subscribe-inspector-to-event.py
echo "rm *.py"
rm *.py
echo "cd .."
cd ..
echo "Completed building distribution"
cd $deployment_dir
