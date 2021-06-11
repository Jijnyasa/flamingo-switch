# Flamingo Switch

## Problem Context

A preprod testing is required even if we have some good testing methods such as local/vm dev box and junits. The preprod testing may be cumbersome in ways mentioned below -

- Teamcity builds are time consuming and some are synchronous eg.common and dependent components.
- Code may be bogous and could take out the whole system down and block others
- Deployment is time consuming
- People having code in a system need to redeploy if someone has tested earlier with their changes

## Proposal

Proposal is to make a client system which would handle all this stuff very quickly and in a resource efficient manner. This application could be used to test applications very quickly and without blocking others.Using this we could switch the host in which we want to deploy and do it so without building teamcity builds and using deployment console. The technology is also used to solve problems that are created by technology. The idea is to solve problems and hide complex details from the developer.T his would contain switches for each of the components. Some of the features include

- Config Reload - Many applications require config changes and still many developers use the builds, deployments to fix configs and perform testing. The idea is to test configs very quickly without dealing with complexities of config paths, docker containers etc.
- Deploy - Deploy components quickly to preprod quickly with a matter of click by just specifying the version or the jar location.
- Patch - We could patch the containers in the host without ever doing a jar deployment. I found the approach was quite tedious and hectic to perform but its still far better than the complete deployements itself. Idea is to patch the application with a click by just specifying the file path to be patched.
- Undeploy - Everyone wants to keep preprod in the state in which they find the environment but they are too lazy to deploy the previous versions. This would give developers the power to undeploy the components at a single click.

## Design Specifications

- The application should have retry mechanisms as networks could be glitchy
- Make the configurations (config paths, jar paths, components list) configurable and loosely coupled with application itself
- Step mechanism to continue or stop at any particular step

## How this will look 

![Screenshot 2021-06-09 at 11 24 05 AM](https://user-images.githubusercontent.com/46473694/121730907-e744ef00-cb0d-11eb-8cbb-e7c8477d8da8.png)
