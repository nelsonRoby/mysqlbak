### 基于python数据库备份恢复脚本

1.原理

采用全量备份整个数据库，以及备份binlog日志，恢复采用备份包解压恢复，再导入备份的binlog日志。

2.使用方法

修改配置文件config.ini

定时执行python dbbackup.py
