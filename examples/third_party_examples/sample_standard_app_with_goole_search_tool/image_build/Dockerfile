FROM docker.io/library/centos:centos8.4.2105
MAINTAINER fanen.lhy@antgroup.com

ARG PROJECT_NAME

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*; \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*; \
    yum install -y wget; \
    yum install -y unzip; \
    yum install -y vim; \
    yum install -y jq; \
    yum install -y net-tools; \
    yum install -y langpacks-zh_CN; \
    yum clean all; \
    mkdir -p /usr/local/etc/workspace/shell; \
    mkdir -p /usr/local/etc/workspace/project; \
    sed -i 's/^LANG=.*/LANG="zh_CN.UTF-8"/' /etc/locale.conf

ENV TZ=Asia/Shanghai
ENV PROJECT_NAME=${PROJECT_NAME}

COPY ./shell /usr/local/etc/workspace/shell/
# Copy project files excluding the image_build directory
COPY ./project_files/ /usr/local/etc/workspace/${PROJECT_NAME}
RUN rm -rf /usr/local/etc/workspace/${PROJECT_NAME}/image_build

RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    /bin/bash /usr/local/etc/workspace/shell/install_python.sh -p 3.10

RUN mkdir -p ~/.pip; \
    echo '[global]'>>~/.pip/pip.conf; \
    echo 'index-url = https://mirrors.aliyun.com/pypi/simple/ '>>~/.pip/pip.conf; \
    /bin/bash --login -c "pip install poetry==1.8.0"; \
    # Install dependencies from pyproject.toml
    cd /usr/local/etc/workspace/${PROJECT_NAME} && \
    /bin/bash --login -c "poetry config virtualenvs.create false && poetry install --no-root"

WORKDIR /home

ENTRYPOINT ["/bin/bash","--login", "/usr/local/etc/workspace/shell/start.sh"]
