#!/usr/bin/env bash

echo 'Start!'

update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2

#cd /vagrant

apt-get update
apt-get install tree

# 安装配置mysql8
if ! [ -e /vagrant/mysql-apt-config_0.8.15-1_all.deb ]; then
	wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb
fi

dpkg -i mysql-apt-config_0.8.15-1_all.deb
DEBIAN_FRONTEND=noninteractivate apt-get install -y mysql-server
apt-get install -y libmysqlclient-dev

if [ ! -f "/usr/bin/pip" ]; then
  apt-get install -y python3-pip
  apt-get install -y python-setuptools
  ln -s /usr/bin/pip3 /usr/bin/pip
else
  echo "pip3 已安装"
fi

# 升级pip，目前存在问题，read timed out，看脸，有时候可以，但大多时候不行
python -m pip install --upgrade pip
# 换源完美解决
# 安装pip所需依赖
pip install --upgrade setuptools # -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --ignore-installed wrapt # -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装pip最新版
pip install -U pip # -i https://pypi.tuna.tsinghua.edu.cn/simple
# 根据 requirements.txt 里的记录安装 pip package，确保所有版本之间的兼容性
pip install -r requirements.txt # -i https://pypi.tuna.tsinghua.edu.cn/simple


# 设置mysql的root账户的密码为yourpassword
# 创建名为twitter的数据库
mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF
# fi


# 如果想直接进入/vagrant路径下
# 请输入vagrant ssh命令进入
# 手动输入
# 输入ls -a
# 输入 vi .bashrc
# 在最下面，添加cd /vagrant

echo 'All Done!'