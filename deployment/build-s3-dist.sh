#!/bin/bash
#
# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh source-bucket-base-name trademarked-solution-name version
#
# Paramenters:
#  - source-bucket-base-name: Name for the S3 bucket location where the template will source the Lambda
#    code from. The template will append '-[region_name]' to this bucket name.
#    For example: ./build-s3-dist.sh solutions server-fleet-management-at-scale v1.0.2
#    The template will then expect the source code to be located in the solutions-[region_name] bucket
#
#  - trademarked-solution-name: name of the solution for consistency
#
#  - version-code: version of the package

# Check to see if input has been provided:
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Please provide the base source bucket name, trademark approved solution name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions server-fleet-management-at-scale v1.0.2"
    exit 1
fi

deployment_dir="$PWD"
template_dist_dir="$deployment_dir/global-s3-assets"
build_dist_dir="$deployment_dir/regional-s3-assets"
source_dir="$deployment_dir/../source"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $template_dist_dir"
rm -rf $template_dist_dir
echo "mkdir -p $template_dist_dir"
mkdir -p $template_dist_dir
echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

echo "------------------------------------------------------------------------------"
echo "[Packing] Templates"
echo "------------------------------------------------------------------------------"
echo "cp $deployment_dir/server-fleet-management-at-scale.yaml $template_dist_dir/server-fleet-management-at-scale.template"
cp $deployment_dir/server-fleet-management-at-scale.yaml $template_dist_dir/server-fleet-management-at-scale.template
echo "cp $deployment_dir/server-fleet-management-at-scale-inspector.yaml $build_dist_dir/server-fleet-management-at-scale-inspector.template"
cp $deployment_dir/server-fleet-management-at-scale-inspector.yaml $build_dist_dir/server-fleet-management-at-scale-inspector.template

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OS
    echo "Updating code source bucket in template with $1"
    replace="s/%%BUCKET_NAME%%/$1/g"
    echo "sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template
    replace="s/%%SOLUTION_NAME%%/$2/g"
    echo "sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template
    replace="s/%%VERSION%%/$3/g"
    echo "sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i '' -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i '' -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template

else
    # Other linux
    echo "Updating code source bucket in template with $1"
    replace="s/%%BUCKET_NAME%%/$1/g"
    echo "sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template
    replace="s/%%SOLUTION_NAME%%/$2/g"
    echo "sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template
    replace="s/%%VERSION%%/$3/g"
    echo "sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template"
    sed -i -e $replace $template_dist_dir/server-fleet-management-at-scale.template
    echo "sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template"
    sed -i -e $replace $build_dist_dir/server-fleet-management-at-scale-inspector.template
fi

echo "------------------------------------------------------------------------------"
echo "[Packing] Lambda functions"
echo "------------------------------------------------------------------------------"
cd $source_dir
echo "zip $build_dist_dir/sfm-custom-resource.zip sfm-custom-resource.py"
zip $build_dist_dir/sfm-custom-resource.zip sfm-custom-resource.py
echo "zip $build_dist_dir/sfm-respond-to-inspector-agent-id-findings.zip sfm-respond-to-inspector-agent-id-findings.py"
zip $build_dist_dir/sfm-respond-to-inspector-agent-id-findings.zip sfm-respond-to-inspector-agent-id-findings.py
echo "zip $build_dist_dir/sfm-respond-to-inspector-assessment-complete.zip sfm-respond-to-inspector-assessment-complete.py"
zip $build_dist_dir/sfm-respond-to-inspector-assessment-complete.zip sfm-respond-to-inspector-assessment-complete.py
echo "zip $build_dist_dir/sfm-subscribe-inspector-event.zip sfm-subscribe-inspector-event.py"
zip $build_dist_dir/sfm-subscribe-inspector-to-event.zip sfm-subscribe-inspector-to-event.py
