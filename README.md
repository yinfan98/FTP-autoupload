## FTP-upload
- 服务器端的文件夹数目需要小于本地文件夹数目
- 配置文件放在和.py文件同一个文件夹中
- 打开终端输入 "crontab -e"  "0 */3 * * * /home/gui/ftp/auto.sh >> /home/gui/ftp/auto.txt"  在定时日志文档中加入这一行 成功设置定时日志
- 在这个文档中有自动化日志  "/home/gui/ftp/auto.txt"  在自动化文档中控制前后进程保证不冲突
- 不要移动 config.yaml
-  pip install -r requirement.txt 安装依赖包
