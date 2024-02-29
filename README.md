# File System-SecFS

**Project Source：MIT 6.858 && OUC 2023《Integrated practice of computer systems》**

**完成时间：2023.08**

### 1、项目介绍

​        本项目构建了一个远程文件系统 SecFS，它在面对完全不受信任的服务器时能提供机密性和完整性。我们为你提供了一个具有很少功能和更少安全保证的框架为基础进行本实验。你需要扩展这些功能来实现线面的实验目标。我们提供的代码是 SUNDR 序列化版本的一部分。你应该阅读论文 SUNDR ，因为本实验中的许多概念和原理与之相似。为了完成本实验，你需要实现其余部分以支持整个序列化 SUNDR，并添加机密性保证（文件的读取保护）。

注：**本人补全了secfs/fs.py文件中的_create的函数，完善文件系统创建文件和目录的功能。**小组成员三人共同修改了secfs/tables.py中的pre()和post()函数，并在secfs/crypto.py中实现了加密操作。共同完善了实验中的代码并进行了测试。

### 2、实验内容

1、实现文件系统对多客户端的支持。首先补全secfs/fs.py文件中的_create 的函数，完善文件系统创建文件和目录的功能。代码如下。

![img](https://github.com/andone-07/File-System-SecFS/blob/master/image/%E5%9B%BE%E7%89%871.png) 

2、之后将新创建的inode保存到server。i-table被持久保存在服务器上，通过version structure更改user和group的i-tables。VSL作为一个字段元组列表实现，类似于SUNDR论文，但只跟踪最近的VS。通过对VS元组的非签名部分进行非对称加密来验证签名。用户的更新将包括所有组i句柄，以便处理同一用户的多个更新，而不会覆盖以前的更新。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps17.jpg) 

3、签名与验证的实现利用利用Cryptography库的签名与验证函数。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps18.jpg)![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps19.jpg) 

4、更新版本结构（Version Structure），更新前签名，拿vs与过去用户手上的vs做对比，最后更新用户的vs。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps20.jpg) 

5、在pre中，获得全局锁，执行文件操作之前，调用pre，获取VSL，更新current_itable使用了VSL中的fetch_vs获取专有用户的VS，使用了查找到所有的group_handle的函数。post中释放锁，更新服务器上的VSL。最后更新用户手上的VSL。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps21.jpg) 

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps22.jpg) 

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps23.jpg) 

6、在crypto中实现加密和解密。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps24.jpg)![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps25.jpg) 

### 3、实验结果 

1、创建文件或文件夹。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps26.jpg)![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps27.jpg) 

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps28.jpg) 

2、运行./test.sh。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps29.jpg) 

3、运行./test-all.sh。

![img](file:///C:\Users\26797\AppData\Local\Temp\ksohtml8256\wps30.jpg) 

### 4、心得总结

​        通过补充完善实现secfs的代码，我深刻理解了secfs文件系统的框架以及交互过程，切实了解了文件的操作是怎么一步一步完成的。实验过程中也遇到了一些问题，例如在完善任务一代码后测试test时，未测试完便出现报错，在查找网络上一些文献后已解决。

​        总的来说，通过这次实验，我对在操作系统中所学习的文件以及文件系统知识的理解更加深刻，了解及学习基于inode和块的文件系统的相关理论知识，收获颇多。

