# Docker container deployment

agentUniverse provides standard work environment images for the containerized deployment of agentUniverse projects. This document will explain how to deploy your own project using such images. You can find the full tag list on  [this site](https://cr.console.aliyun.com/repository/cn-hangzhou/agent_universe/agent_universe/images). If you want to package an image based on your own project, please refer to [Project Image Packaging](./Project_Image_Packaging.md).

## Preparations
1.  Build your own project according to the standard directory structure of agentUniverse, referring to the [Application_Engineering_Structure_Explanation](../../../en/Get_Start/1.Application_Project_Structure_and_Explanation.md). For ease of explanation, this document assumes the project name and project directory are `sample_standard_app`.
2.   Obtain the required version of the AagentUniverse image.
```shell
docker pull registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8
```


## Method 1: Mount the host path
You can mount your project to a path inside the container by mounting the host directory. The reference command is as follows:
```shell
docker run -d -p 8888:8888 -v ./sample_standard_app/:/usr/local/etc/workspace/project/sample_standard_app registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8
```
The`-p 8888:8888`represents the port mapping for the Web Server. The first 8888 indicates that the web server inside the container is started on port 8888, and the latter indicates that it is mapped to port 8888 on the host machine. Adjust it according to the actual startup conditions of your application as needed.  
`-v {local_dir}:/usr/local/etc/workspace/project/{local_dir_name}`indicates that the `local_dir` directory on the host is mounted to the `/usr/local/etc/workspace/project`within the container. The directory path inside the container is a fixed value and cannot be modified. `local_dir_name` stands for the last pattern of the `local_dir`.

### Precautions:：
If you need multiple containers to mount the same directory, consider the following points when using this method:：
1. Specify a SQLite database file address outside the mounted path `/usr/local/etc/workspace/project`in the config.toml, such as inside `/usr/local/etc` in the container, for example,
    ```toml
    system_db_uri = 'sqlite:////usr/local/etc/agent_universe.db'
    ```
    This can reduce issue with SQLite concurrency (as SQLite does not handle concurrency very well). Alternatively, you can directly use MySQL, which offers better concurrency performance.
2. Specify a directory outside the mounted path in the log_config.toml, like:
    ```toml
    log_path = "/usr/local/etc/au_log"
    ```
    To prevent all containers from logging to the same file, which makes it difficult to read.

## Method 2: Pull the project from Github
The image already has the git command installed. You can modify the image's entrypoint to git clone your project and then copy the entire project to a specified path. For example:
```shell
docker run -d -p 8888:8888 --entrypoint=/bin/bash registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8 -c "git clone {repo_addr}; mv {project_dir} /usr/local/etc/workspace/project; /bin/bash --login /usr/local/etc/workspace/shell/start.sh"
````
Where `repo_addr` is the address of your git project，and `project_dir` is the project directory, for example，if `sample_standard_app` is in the `project`directory within your git project, then`project_dir` would be `project/sample_standard_app`。
## Result Verification
Using port 8888 as an example, you can verify whether the service has started correctly using the curl command:
```shell
curl http://127.0.0.1:8888/echo
```
Try to access the web service. If it returns the word "Welcome", it means the service has started successfully.
