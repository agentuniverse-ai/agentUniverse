#!/bin/bash
set -euo pipefail

MINIFORGE_VERSION="26.3.2-3"
MINIFORGE_INSTALLER="Miniforge3-${MINIFORGE_VERSION}-Linux-x86_64.sh"
MINIFORGE_SHA256="848194851a98903134187fbb4ab50efe87b003e0c0f808f97644b7524a62bf2c"
MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE_VERSION}/${MINIFORGE_INSTALLER}"

wget -O "${MINIFORGE_INSTALLER}" "${MINIFORGE_URL}"
echo "${MINIFORGE_SHA256}  ${MINIFORGE_INSTALLER}" | sha256sum -c -
chmod +x "${MINIFORGE_INSTALLER}"
"./${MINIFORGE_INSTALLER}" -b -p /usr/local/etc/workspace/miniforge

/usr/local/etc/workspace/miniforge/bin/conda init
source /root/.bashrc
echo 'channels:
- defaults
show_channel_urls: true
default_channels:
- https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
- https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
- https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
' >~/.condarc

conda config --set show_channel_urls yes
conda clean -i -y

while getopts ":p:" opt; do
  case $opt in
  p)
    if [ "$OPTARG" == "3.10" ]; then
      conda create -y -c conda-forge -n agentuniverse310 python=3.10
    fi
    ;;
  esac
done

echo "conda activate agentuniverse310" >>/root/.bashrc
/bin/bash -c "/usr/local/etc/workspace/miniforge/bin/conda init"
