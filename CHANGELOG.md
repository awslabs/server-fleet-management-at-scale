# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2019-12-20
### Added
- Add ```CHANGELOG.md```
- Add ```sfm-custom-resource.py``` for the common custom resources
- Add KMS custom key for Amazon Simple Notification Service

### Updated
- Update ```build-s3-dist.sh``` script
- Update ```README.md``` to reflect the latest information
- Update software license
- Update AWS CloudFormation templates: cfn_nag_scan suppress rules, custom resources, and reflecting latest information
- Update AWS CloudFormation templates: Pulled out policies from roles
- Update ```sfm-subscribe-inspector-to-event.py```: send function and logging level to INFO
- Update Amazon Simple Notification Service to use custom key

### Removed
- Remove unnecessary codes
- Remove ```Runtime Behavior Rules Package``` from Amazon Inspector since it is no longer supported

## [1.1.0] - 2018-06-28
### Added
- Add resource data sync feature

## [1.0.0] - 2018-06-05
### Added
- Server Fleet Managemant at Scale release