#!/usr/bin/env bash

echo 'Start!'

update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2

#cd /vagrant

apt-get update
apt-get install tree

# mysql8
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

# update pip，
python -m pip install --upgrade pip

pip install --upgrade setuptools # -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --ignore-installed wrapt # -i https://pypi.tuna.tsinghua.edu.cn/simple
# pip newest
pip install -U pip # -i https://pypi.tuna.tsinghua.edu.cn/simple
# install pip package
pip install -r requirements.txt # -i https://pypi.tuna.tsinghua.edu.cn/simple

service mysql start

# 设置mysql的root账户的密码为yourpassword
# 创建名为twitter的数据库
mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF

python manage.py migrate

# fi
# superuser名字
USER="admin"
# superuser密码
PASS="admin"
# superuser邮箱
MAIL="admin@twitter.com"
script="
from django.contrib.auth.models import User;

username = '$USER';
password = '$PASS';
email = '$MAIL';

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell


# 如果想直接进入/vagrant路径下
# 请输入vagrant ssh命令进入
# 手动输入
# 输入ls -a
# 输入 vi .bashrc
# 在最下面，添加cd /vagrant

echo 'All Done!'
