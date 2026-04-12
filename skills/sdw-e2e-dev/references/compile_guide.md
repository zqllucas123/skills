代码编译指南：

## 提交git
在完成某个功能模块的编码工作后，需自动提交更新到远程代码仓库

## 创建端口映射关系
先读取/Users/lucaszhou/.sdw/prj/projects.json 中与当前项目匹配的deploy_config信息，如果之前没有创建远程端口映射关系则建立远程部署服务端口到本地端口的映射关系    
 "connect_port": "22",
"deploy_service_ip": "10.10.13.149",
"deploy_service_port": "8000",
"password": "sdw@2026",

## 调用预编译接口得到编译日志
调用下述接口，下述18000为建立的本地端口映射
curl -X 'POST' \
  'http://127.0.0.1:18000/compile' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "local_source_path": "D:\\works\\sdw_coder\\auto_drive\\Fusion_api",
  "remote_path": "/root/auto_drive/APA_PerceptionFusion",
  "docker_container": "auto_drive_v2",
  "docker_work_dir": "/APA_PerceptionFusion",
  "build_command": "./build_on_docker.sh linux-x86",
  "build_server_host": "192.168.52.248",
  "build_server_port": 22,
  "build_server_user": "root",
  "build_server_password": "ocsa@2026!",
  "proxy_host": "127.0.0.1",
  "proxy_port": 1080,
  "proxy_type": "http"
}'
返回值为编译日志信息