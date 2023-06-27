from ftplib import FTP
import os
import sys
import yaml
import re
from datetime import datetime
ftp = FTP()
########################加载库
class ftpopt(object):
    def __init__(self): #在初始函数中读取yaml文件

        connuse = yamlopt('Connection')
        self.con = connuse.yamlRead()
        locuse = yamlopt('Local')
        self.loc = locuse.yamlRead()
        ftpuse = yamlopt('Ftp')
        self.fftp = ftpuse.yamlRead()
        diruse = yamlopt('sub')
        self.dirnameuse = diruse.yamlRead()

    def ftpconnect(self): #建立连接文件 连接所需参数保存在yaml中
        con = self.con  #获取连接信息
        try:
            ftp.connect(con[0], 21) #建立服务器连接
            ftp.login(con[2], con[3]) #登录信息
            print('*************************connect success******************\n\n')
        except:
            print('login failed,please check')
            exit()
        ftp.cwd(self.fftp) #进入需要操作的文件夹

    def ftpclean(self):
        ftp.cwd(self.fftp)
        print('clean now list {}'.format(self.fftp))
        g = ftp.nlst()
        for i in range(len(g)):
            try:
                ftp.cwd(self.fftp + g[i])
            except:
                print('there some file but not dir')
                ftp.delete(self.fftp + g[i])
        print('clean finished!\n')


class fileopt(ftpopt):

    def get_day(self): #获取当日时间信息
        now = datetime.now()
        now_day = now.strftime('%m%d')
        return now_day

    def get_ftp_dir(self): #获取服务器操作根目录下地址，因为在24行已经进行cwd操作，所以此处不用再进行cwd
        ftp.cwd(self.fftp)
        list = ftp.nlst()
        return list

    def get_local_dir(self): #获取本地地址
        list = os.listdir(self.loc) #列出本地文件夹
        llist = []
        for i in range (len(list)):
            new_list = re.match(r'(\w{4})(\w{4})',list[i]) #用正则表达式匹配本地文件夹
            llist.append(new_list.group(2))
        return llist #把本地文件夹以MMDD的形式写入数组中

    def contrastdir(self):
        lo = self.get_local_dir() #获取本地文件夹数组
        ftpp = []
        for i in range(len(self.get_ftp_dir())): #匹配ftp服务器上已有的文件夹
            ftpp_lin = re.match(r'(\w{3}\_\w{4}\_)(\w{4})',self.get_ftp_dir()[i])
            ftppo = ftpp_lin.group(2)
            ftpp.append(ftppo)
    #    day = self.get_day() #获得本日日期
        not_finish_list = [] #提前建立数组
        day_question_up_list = []
        lot = []
        if len(lo) >= len(ftpp):
            for i in range(len(lo)): #准备建立文件夹
                if lo[i] not in ftpp: #ftp上没有的文件夹 则建立文件夹
                    ftp.cwd(self.fftp)
                    mkd_add = str(self.dirnameuse[1]) + lo[i]
                    ftp.mkd(mkd_add)
                
                mkd_add = self.dirnameuse[1] + lo[i]
                cwd_list = os.path.join(self.fftp,mkd_add)
                ftp.cwd(cwd_list)
                isfree = ftp.nlst()
                if isfree: #文件夹内有文件则判断为一天没传
                    lloc_path = self.loc + str(self.dirnameuse[0])
                    loc_path = lloc_path + lo[i]
                    loc_file = os.listdir(loc_path)
                    if len(loc_file) > len(isfree):
                        not_finish_list.append(lo[i]) #没传完

                    elif len(loc_file) == len(isfree):
                        print('{}日所有文件都已传完'.format(lo[i]))
                        lot.append(lo[i])

                    else:
                        print('本地文件缺失')
                if not isfree: #文件夹内没文件 且文件夹名字不是今天
                    day_question_up_list.append(lo[i]) #有一天没传


        else:
            print('some thing wrong with the save file')
        return not_finish_list,day_question_up_list,lot

    def pro_get(self): #给不同问题建立不同文件夹并返回控制值
        pro_1,pro_2,e = self.contrastdir()
        if not pro_1 and not pro_2:
            final_start = []
            final_start_1 = []
            final_start_2 = []
            token = -1 #-1 都传完了
            
        elif  pro_1 and not pro_2:
            final_start = []
            final_start_1 = []
            final_start_2 = []
            token = 1 #1,有问题，文件夹内没全上传完成
            for i in range(len(pro_1)): #判断文件夹内哪些文件没完全上传
                final_start.append(pro_1[i])
                if len(pro_1) > 1:
                    thread = len(pro_1)
                else:
                    thread = 1
        elif not pro_1 and pro_2:
            final_start = []
            final_start_1 = []
            final_start_2 = []
            token = 2 #有问题，某日文件全部没有上传
            for i in range(len(pro_2)):
                final_start.append(pro_2[i])
        elif pro_1 and pro_2:
            final_start = []
            final_start_1 = []
            final_start_2 = []
            token = 3 #有大问题 有一天文件夹空着并且另一个文件夹有没有上传的文件
            for i in range(len(pro_1)):
                final_start_1.append(pro_1[i])
            for i in range(len(pro_2)):
                final_start_2.append(pro_2[i])
        print(final_start,final_start_1,final_start_2,token)
        return final_start,final_start_1,final_start_2,token,e



class getlist(ftpopt):



    def ReadList(self,u): #获取上传时本地的具体地址，并存成一个数组
        path_listt = os.path.join(self.loc,u)
        path_listtt = path_listt + '/'
        path_list = os.listdir(path_listtt)
        path_list_full = []
        for i in range(len(path_list)):
            path_list_full.append(os.path.join(path_listtt,path_list[i]))
        return path_list,path_list_full

    def SaveList(self,u): #获取上传时服务器的具体地址，并存成一个数组
        path_listt = os.path.join(self.loc, u)
        path_listtt = path_listt + '/'
        save_count = os.listdir(path_listtt)
        save_full = []
        ftp_root = self.fftp + u
        ftp_roott = ftp_root + '/'
        for i in range(len(save_count)):
            path_sh = ftp_roott + str(save_count[i])
            save_full.append(path_sh)
        return save_full,save_count


class ftpp_up(getlist):


    def __init__(self):
        gl = fileopt()
        self.a,self.b,self.c,self.i,self.e = gl.pro_get()
        self.day = gl.get_day()

        connuse = yamlopt('Connection')
        self.con = connuse.yamlRead()
        locuse = yamlopt('Local')
        self.loc = locuse.yamlRead()
        ftpuse = yamlopt('Ftp')
        self.fftp = ftpuse.yamlRead()
        diruse = yamlopt('sub')
        self.dirnameuse = diruse.yamlRead()


    def codeup(self): #根据不同的控制指令进行上传




        if self.i == 2: #指令2
            for i in range(len(self.a)):
                print('{}日文件上传'.format(self.a[i]))
                goftppath22 = self.fftp + self.dirnameuse[1]
                goftppath2 = goftppath22 + self.a[i]
                ftp.cwd(goftppath2)
                usepa = str(self.dirnameuse[0]) + self.a[i]
                nouse, uppath = self.ReadList(usepa)
                ftppath, nouse1 = self.SaveList(usepa)
                for j in range (len(uppath)):
                    self.ftp_up(uppath[j],nouse1[j])
                print('{}日文件上传成功，待检测'.format(self.a[i]))

        elif self.i == 1: #指令1
            for i in range(len(self.a)):
                print('{}日文件未上传完全'.format(self.a[i]))
                goftppath11 = self.fftp + self.dirnameuse[1]
                goftppath1 = goftppath11 + self.a[i]
                ftp.cwd(goftppath1)
                loc11 = self.loc + str(self.dirnameuse[0])
                loc = loc11 + self.a[i]
                loc_dir = os.listdir(loc)
                ftp_dir = ftp.nlst()
                for j in range(len(loc_dir)):
                    if loc_dir[j] not in ftp_dir:
                        local1 = loc + '/'
                        local = local1 + loc_dir[j]
                        self.ftp_up(local,loc_dir[j])
                print('{}日文件补全成功'.format(self.a[i]))

        elif self.i == 3: #指令3
            for i in range(len(self.c)):    #先处理完全没有上传的文件
                goftppath311 = self.fftp + self.dirnameuse[1]
                goftppath31 = goftppath311 + self.c[i]
                ftp.cwd(goftppath31)
                print('{}日文件上传'.format(self.c[i]))
                usepa = str(self.dirnameuse[0]) + self.c[i]
                nouse, uppath = self.ReadList(usepa)
                ftppath, nouse1 = self.SaveList(usepa)
                for j in range(len(uppath)):
                    self.ftp_up(uppath[j], nouse1[j])
                print('{}日文件上传成功，待检测'.format(self.c[i]))

            for i in range(len(self.b)):
                print('并且{}日未上传完全'.format(self.b[i]))
                goftppath322 = self.fftp + self.dirnameuse[1]
                goftppath32 = goftppath322 + self.b[i]
                ftp.cwd(goftppath32)
                loc33 = self.loc + str(self.dirnameuse[0])
                loc = loc33 + self.b[i]
                loc_dir = os.listdir(loc)
                ftpp = os.path.join(self.fftp, self.b[i])
                ftp_dir = ftp.nlst()
                for j in range(len(loc_dir)):
                    if loc_dir[j] not in ftp_dir:
                        local3 = loc + '/'
                        local = local3 + loc_dir[j]

                        self.ftp_up(local,loc_dir[j])
                print('{}日文件补全成功'.format(self.b[i]))

        elif self.i == -1:
            print('所有文件都已上传完成，check\n')




    def ftp_up(self,filename,remote_pic): #上传模块

        bufsize = 1024
        with open(filename,'rb') as pic:
            ftp.storbinary('STOR %s' % remote_pic,pic,bufsize)

        print("ftp up {} OK to {}".format(filename,remote_pic))



    def ftp_quit(self): #退出模块
        ftp.quit()

class yamlopt(object):

    def __init__(self,order): #通过order指令读取yaml文件中不同的参数
        self.order = order

    def yamllist(self): #获取yaml文件的地址

        
        path_1 = os.getcwd()
        path = os.path.join(path_1,'config.yaml')
        return path

    def yamlRead(self): #根据指令进行读取

        path = self.yamllist()
        f = open (path,'r',encoding='utf-8')
        con = f.read()
        x = yaml.load(con,Loader=yaml.FullLoader)
        if self.order == 'Ftp': #读取ftp模块
            updateaddress = x['Ftp']['update_add']
            return updateaddress
        elif self.order == 'Local': #读取本地模块
            updateaddress2 = x['Local']['local_add']
            return updateaddress2
        elif self.order == 'Connection': #读取登录模块
            con = []
            ipad = x['Connection']['Ip']
            port = x['Connection']['port']
            userid = x['Connection']['userid']
            password = x['Connection']['pwd']
            con.append(ipad)
            con.append(port)
            con.append(userid)
            con.append(password)
            return con
        elif self.order == 'sub':
            subb = []
            subftp = x['sub']['subftpname']
            subloc = x['sub']['sublocname']
            subb.append(subloc)
            subb.append(subftp)
            return subb
        else:
            return False


class test(ftpp_up):

    def contrastdir(self):
        pass

    def contr(self):


        if self.i == 1 or self.i == 2:
            print('错误1，2检测')
            for i in range(len(self.a)):
                q12loc1 = self.loc + str(self.dirnameuse[0])
                q12loc = q12loc1 + self.a[i]
                q12ftp1 = self.fftp + self.dirnameuse[1]
                q12ftp = q12ftp1 + self.a[i]
                q12loclist = os.listdir(q12loc)
                ftp.cwd(q12ftp)
                q12ftplist = ftp.nlst()
                if len(q12loclist) == len(q12ftplist):
                    print('upload success 12')
                elif len(q12loclist) > len(q12ftplist):
                    print('something upload failed,re upload')
                    self.reload(q12loc,q12ftp)
                else:
                    print('file wrong {}'.format(self.a[i]))
        elif self.i == 3:
            for i in range(len(self.b)):
                q12loc1 = self.loc + str(self.dirnameuse[0])
                q12loc = q12loc1 + self.b[i]
                q12ftp1 = self.fftp + self.dirnameuse[1]
                q12ftp = q12ftp1 + self.b[i]
                q12loclist = os.listdir(q12loc)
                ftp.cwd(q12ftp)
                q12ftplist = ftp.nlst()
                if len(q12loclist) == len(q12ftplist):
                    print('upload success 1')
                elif len(q12loclist) > len(q12ftplist):
                    print('something upload failed,re upload')
                    self.reload(q12loc, q12ftp)
                else:
                    print('file wrong {}'.format(self.b[i]))
            for i in range(len(self.c)):
                q12loc1 = self.loc + str(self.dirnameuse[0])
                q12loc = q12loc1 + self.c[i]
                q12ftp1 = self.fftp + self.dirnameuse[1]
                q12ftp = q12ftp1 + self.c[i]
                q12loclist = os.listdir(q12loc)
                ftp.cwd(q12ftp)
                q12ftplist = ftp.nlst()
                if len(q12loclist) == len(q12ftplist):
                    print('upload success 2')
                elif len(q12loclist) > len(q12ftplist):
                    print('something upload failed,re upload')
                    self.reload(q12loc, q12ftp)
                else:
                    print('file wrong {}'.format(self.c[i]))

        print('\n*************************检测完成,exit**********************')

    def reload(self,loc,ftpr):
        print('本次文件上传有遗漏{}'.format(loc))
        loc_dir = os.listdir(loc)
        ftp.cwd(ftpr)
        ftp_dir = ftp.nlst()
        for i in range(len(loc_dir)):
            if loc_dir[i] not in ftp_dir:
                locall = loc + '/'
                local = locall + loc_dir[i]
                fftpp = ftpr + '/'
                fftp = fftpp + loc_dir[i]

                self.ftp_up(local, loc_dir[i])



if __name__ == '__main__':
    conne = ftpopt()  #连接
    
    conne.ftpconnect()
    conne.ftpclean()

    ftpup = ftpp_up() #上传
    ftpup.codeup()
    lasttest = test()
    lasttest.contr()
    ftpup.ftp_quit()
    


#################下载
