# my_flask_ecs_obs
研究和实现一个基于云计算的图片分类系统。学习Flask框架的应用及MongoDB和华为云服务ECS，OBS的使用，探索云计算在图片处理中的实际应用，提升对云服务和机器学习技术的综合运用能力。调用VGG16接口。


在本地flask框架上，用户输入账号密码登录进入分析页，由mongodb服务器进行登陆验证，并将登陆时间记录在数据库中。
接着用户上传图片到obs桶上，上传文件名给云服务器，云服务器端根据文件名获取obs桶上图片的地址进行识别分析，再将识别结果传送给本地，在本地展示。本地也可以查看所有用户和最后登录时间。


markupsafe==2.0.1

keras==2.8.0 

tensorflow==2.8.0

esdk-obs-python --trusted-host pypi.org
