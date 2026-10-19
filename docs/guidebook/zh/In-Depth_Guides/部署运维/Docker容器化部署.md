# Docker容器化部署

agentUniverse提供标准的工作环境镜像用于容器化部署agentUniverse工程。本文档将介绍如何基于工作环境镜像部署您自己的工程项目。镜像tag列表可以在[这里获取](https://cr.console.aliyun.com/repository/cn-hangzhou/agent_universe/agent_universe/images)。如果您希望打包一个基于自己工程的镜像，请参考[工程镜像打包](./工程镜像打包.md)。

## 准备工作
1.  按照agentUniverse的标准结构目录搭建自己的项目，具体结构参考[应用工程结构及说明](../../../zh/开始使用/1.标准应用工程结构说明.md)。为方便说明，在本文档中假设项目名称和工程目录为`sample_standard_app`。
2.  获取所需版本的镜像:
```shell
docker pull registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8
```


## 方法一：挂载宿主机路径
您可以通过将宿主机目录挂载您的项目至容器内路径，参考命令如下:
```shell
docker run -d -p 8888:8888 -e OPENAI_API_KEY=XXX -v ./sample_standard_app/:/usr/local/etc/workspace/project/sample_standard_app registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8
```
其中`-p 8888:8888`为Web Server的端口映射，前面的8888表示容器内的webserver启动在8888端口，后者表示映射到宿主机的8888端口，可自行根据实际应用的启动情况调整。-e OPENAI_API_KEY=XXX可以添加容器内的环境变量。  
`-v {local_dir}:/usr/local/etc/workspace/project/{local_dir_name}`表示把本地`local_dir`目录挂载至容器内的`/usr/local/etc/workspace/project`目录，容器内目录为固定值，不可修改,`local_dir_name`表示你本地文件夹的名字，也就是`local_dir`的最后一级目录名称。

### 使用多个容器挂载相同目录时，有以下几点建议：
由于多个容器在相同的挂载目录进行文件的读写，有几处设置可以优化并发读写的冲突：
1. 当您使用本地Sqlite库时，sqlite的本地数据库文件默认保存在项目主目录下，因此所有容器会读写同一个数据库文件，可能引发并发问题。建议在config.toml中指定一个非挂载路径 `/usr/local/etc/workspace/project`下的sqlite数据库文件地址，如容器内的`/usr/local/etc`下，例如
    ```toml
    system_db_uri = 'sqlite:////usr/local/etc/agent_universe.db'
    ```
    或者也可以使用mysql，避免在本地进行数据库文件的读写。
2. 日志文件输出的默认路径是在项目工程的主目录，也就是挂载目录中，因此推荐在log_config.toml中指定一个非挂载路径下的目录，如
    ```toml
    log_path = "/usr/local/etc/au_log"
    ```
    这样可以避免所有容器日志打印在同一个文件中导致难以阅读。
3. 上述命令的端口映射部分`8888:8888`需要将后面的8888修改为不同端口，否则会发生端口冲突  

## 方法二：从Github拉取项目
镜像中已安装git命令，您可以通过修改镜像的entrypoint，git clone您的项目后将整个工程复制到指定路径，示例命令：
```shell
docker run -d -p 8888:8888 --entrypoint=/bin/bash registry.cn-hangzhou.aliyuncs.com/agent_universe/agent_universe:0.0.14b1_centos8 -c "git clone {repo_addr}; mv {project_dir} /usr/local/etc/workspace/project; /bin/bash --login /usr/local/etc/workspace/shell/start.sh"
````

其中`repo_addr`是你的git项目地址，`project_dir`是工程路径，比如`sample_standard_app`在你git项目下的`project`目录，那么`project_dir`就是`project/sample_standard_app`。
## 结果验证
以该示例中的8888端口为例，您可以通过curl命令验证服务是否正确启动
```shell
curl http://127.0.0.1:8888/echo
```
来尝试访问web服务，如返回Welcome字样则说明服务已启动成功。
