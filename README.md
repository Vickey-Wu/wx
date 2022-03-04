

# install python


## create environment

in centos

```shell
yum install python36u
```

create virtual environment and source

```shell
mkdir -p ~/code/venv
cd ~/code/venv
python3 -m venv wx
source ~/code/venv/wx/bin/activate
```

copy files in this project to server.

firstly, login in your server, then, clone github repository

**todo: push code to github**

```shell
mkdir -p ~/code/wx
cd ~/code/wx
...git clone here...
```

install third requirement
```shell
pip install -r requirements.txt
```

## start flask service

you need set actual info for token, aes_key, appid

if you are in plaintext mode, just set WECHAT_TOKEN is ok.

```shell
export WECHAT_TOKEN=token
export WECHAT_AES_KEY=aes_key
export WECHAT_APPID=appid
```

```shell
cd ~/code/wx
chmod +x restart.sh
./restart.sh
```

the http://0.0.0.0:8081 will work

# install nginx


```shell
yum install nginx
```

vi /etc/nginx/nginx.conf

```shell
http {
...
upstream idlepig {
    server 127.0.0.1:8081;
  }
...
}
```

vi /etc/nginx/conf.d/default.conf

```shell
server {
    listen 80;
    server_name _;
    location / {
      proxy_pass http://idlepig;
    }
}
```

so, we map 80 port to 8081 port

start nginx

```shell
nginx
```

# for WeChat platform

[article_for_wx.py](article_for_wx.py) has chinese comment is only for WeChat platform