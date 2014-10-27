#!/usr/bin/python3

import sys
from urllib.request import *
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os
import imp
import bs4
from mylog import *
from json import *
from traceback import *
from time import *
import urllib.parse
from random import *
import hashlib
from DomainSuffix import DomainSuffix

#imp.reload(sys)
#sys.setdefaultencoding("utf-8")

def get_time_rand ():
    t = int(time());
    t1 = randint(1,999999)
    return str(t)+'_'+str(t1)

def get_img_file_name (title="default"):
    mymd5 = hashlib.md5()
    mymd5.update(title.encode('utf-8'))
    return mymd5.hexdigest()+'_'+get_time_rand ()
    
class WebFetch:
    def __init__ (self):
        self.urls = {}
        self.page_str = None
        self.f = None
        #self.myparser = MyHTMLParser()        
        self.domain = None
        self.ds=DomainSuffix()
        self.load_ret = self.ds.load_file('./domain_suffixes.txt')
        #logging.info('Domain suffix load ret:'+str(self.load_ret))
        self.header_dict = {}
        self.encode = None
        self.cur_url = None
        
        self.img_reg = re.compile("arrayImg\[0\]=\"(.*?)\"")
        #print(ret)
    # self.domain format: qq.com,163.com
    def get_start_domain (self,url):
        self.domain = self.ds.get_top_domain(url)
        if(not isinstance(self.domain,str)): 
            return -1
        else: 
            return self.domain

    def get_start_domain1 (self,url):
        tdomain = self.ds.get_top_domain(url)
        if(not isinstance(tdomain,str)): 
            return -1
        else: 
            return tdomain
    '''
    return value:
    -1 for error. str for success.
    '''
    def get_page (self,url,pdata=None):
        self.page_str = None
        self.cur_url = url
        if(not isinstance(url,str)): 
            logging.error('not isinstance(url,str),url:'+str(url))
            return -1
        f = None
        try:     
           #urllib.parse.quote(purl)  
           header_dict={'User-Agent':\
           'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
           if(pdata is None):
              req = Request(url=url,headers=header_dict)
           elif(isinstance(pdata,dict)):
              tmp_pdata = urllib.parse.urlencode(pdata)
              req = Request(url=url,\
                            data=tmp_pdata.encode(encoding="utf-8",errors="ignore"),\
                            headers=header_dict,method='POST')
           else:
               return -1
           f = urlopen(req,timeout=120) 
           #f=urlopen(url,timeout=120)
        except:
            ex = format_exc()
            logging.error('EXCEPTION:'+ex)
            print('EXCEPTION:'+ex)
            logging.error('urlopen(...),timeout:120,url:'+str(url))
            return -1
        #print(self.f.geturl())
        #print("\n--------------\n")
        #print(self.f.info())        
        h = str(f.headers).lower()
        #print(h)
        #logging.info(h)
        h1 = h.splitlines()
        #print(h1)
        #print('----------------\n')
        d = {}
        for x in h1 :
            #print(x)
            if x!='':
              tmp = x.split(':',1)
              #print(x)
              #print(tmp)
              d[tmp[0]] = tmp[1]
        encode = ''
        if(d['content-type'].rfind('gb')>0):
            encode = 'gb18030'
        elif(d['content-type'].rfind('utf')>0):
            encode = "utf-8"
        else:
            encode = ''

        self.header_dict = d
        #encode=''
        try:
          #print(type(f))
          #6*1024*1024=6291456 500*1024=51200 1024*1024=1048576
          html_bytes = f.read(4*1048576) 
        except:
            logging.error("except:self.f.read().")
            return -1

        if(encode==''):
            head = html_bytes.partition(b'</head>')
            c_idx = head[0].find(b'charset=')
            #print('c_idx:'+str(c_idx))
            #print('head[0]:'+str(head[0])+'')
            tmp_encode = head[0][c_idx:c_idx+20].lower()
            #print('tmp_encode:'+str(tmp_encode))
            if(b'utf' in tmp_encode):
                encode = 'utf-8'
            elif(b'gb' in tmp_encode):
                encode = 'gb18030'
            else:
                encode = ''
            #print(head[0])
        #print('encode:['+encode+']')
        #logging.info('encode:['+encode+']')
        self.encode = encode
        try:
            if(encode == 'gb18030'):
                self.page_str = html_bytes.decode(encode,"ignore").encode('utf-8',"ignore").decode('utf-8',"ignore")           
                return self.page_str.lstrip('\ufeff')
            elif(encode == 'utf-8'): 
                self.page_str = html_bytes.decode(encode,"ignore")
                return self.page_str.lstrip('\ufeff')
            else:
                self.page_str = None
                logging.info('self.page_str=None')
                return -1;
        except:
            self.page_str = None
            logging.info('self.page_str=None')
            return -1
    '''
    return value:
    The full file name for true;
    -1 for error.
    '''
    def get_img (self,url,saved_file_path="default"):
        if(not isinstance(url,str)): 
            logging.error('not isinstance(url,str),url:'+str(url))
            return -1
        f = None
        try:     
           #urllib.parse.quote(url)   
           f = urlopen(url,timeout=120)
        except:
            ex = format_exc()
            logging.error('EXCEPTION:'+ex)
            #print('EXCEPTION:'+ex)
            logging.error('urlopen(...),timeout:120,url:'+str(url)+',continue...')
            if f is not None:
                f.close()
            return -1
        #print(type(f))
        #print(f.headers)
        #print(f.headers.get('Content-Type'))
        content_type = f.headers.get('Content-Type')
        # check whether starting with str 'img'.
        if(not content_type.startswith('image')):
            logging.error('Not img!conteng_type:['+content_type+'] url:'+str(url))
            return -1
        #print(type(content_type))
        #content_type='img/inmg/jpg/png'
        suffix = "." + content_type.rsplit('/',1)[1]
        img_file_name = 'img_' + get_time_rand() + suffix
        file_name = saved_file_path + img_file_name
        #print(suffix)
        f1 = open(file_name,'wb')
        f1.write(f.read())
        f1.close()
        f.close()
        return img_file_name
        

    '''
    return value: -1 for error.
    return self.urls for success, type dict
    '''
    def get_links (self,url=None):
        
        if(url is not None):
            tmp_page_str = self.get_page(url)
            if(tmp_page_str == -1):
                logging.error("(tmp_page_str==-1),url:"+url)
                return -1
            if(self.domain is None):
                self.get_start_domain(url)
        else:
            return None
        #print(self.page_str)
        #os.sys.stdout.buffer.write(text)
       
        tmp_url_dict = {}
        bs = BeautifulSoup(tmp_page_str) #,'lxml'
        #print(bs.a.get_text("|"))        
        #print(bs.find_all('a'))
        #print(bs.body.get_text("|"))
        hrefa = bs.find_all("a")
        for x in hrefa :
            if(x.has_attr('href')):
               if(x["href"].startswith("/")):
                   new_url="http://www."+self.domain+x["href"]
                   tmp_url_dict[new_url] = 1
               elif(x["href"].startswith("http://")):
                   tmp_url_dict[x["href"]] = 1
               elif(x["href"].startswith("../../") or x["href"].startswith("../") or
                    x["href"].startswith("./") ):
                   new_url = x["href"].lstrip('./')
                   new_url = "http://www." + self.domain+'/' + new_url
                   tmp_url_dict[new_url] = 1
               elif(len(x["href"])>3):
                   new_url = "http://www."+self.domain+'/'+x["href"]
                   tmp_url_dict[new_url] = 1
                   #continue
        self.urls = tmp_url_dict
        #print(self.urls)
        return tmp_url_dict
            
    '''
    return : None for error; tmp_img_url_dict for success.
    '''
    def get_img_links (self,url=None):
        tmp_page_str = None
        if(url is not None):
            tmp_page_str = self.get_page(url)
            if(tmp_page_str==-1):
                logging.error("(tmp_page_str==-1)")
                return None
            if(self.domain is None):
                self.get_start_domain(url)
        else: 
            return None
        
        tmp_img_url_dict = {}
        bs = BeautifulSoup(tmp_page_str) 
        href_src = bs.find_all("img")
        for x in href_src :
            if(x.has_attr('src')):
               if(x["src"].startswith("/")):
                   new_url="http://www."+self.domain+x["src"]
                   tmp_img_url_dict[new_url] = 1
               elif(x["src"].startswith("http://")):
                   tmp_img_url_dict[x["src"]] = 1
               elif(x["src"].startswith("../../") or x["src"].startswith("../") or
                   x["src"].startswith("./") ):
                   new_url = x["src"].lstrip('./')
                   new_url = "http://www." + self.domain+'/' + new_url
                   tmp_img_url_dict[new_url] = 1
               elif(len(x["src"])>3):
                   new_url = "http://www."+self.domain+'/'+x["src"]
                   tmp_img_url_dict[new_url] = 1
                   #continue

        js_img_links = self.img_reg.findall(tmp_page_str)
        for tmp_img_url in js_img_links:
            if(tmp_img_url.startswith("http://")):
                tmp_img_url_dict[tmp_img_url] = 1
                logging.info('--->js img url:'+tmp_img_url)
                print('--->js img url:'+tmp_img_url)
        #print(self.urls)
        return tmp_img_url_dict
    '''
    return dict{'title':'title string','meta':{'name':'value','name':'value',...}}
    rerurn -1 for error
    '''
    def get_title_meta (self,url=None):
       if(url is not None):
           self.page_str = self.get_page(url)
           if(self.page_str==-1): 
               logging.error('self.page_str==-1,url:'+self.cur_url)
               return -1 
       elif(self.page_str==-1 or (self.page_str is None)): 
           logging.error('(self.page_str==-1 or (self.page_str is None)),url:'\
                         +self.cur_url)
           return -1

       if(isinstance(self.page_str,str) and len(self.page_str)<50):
           logging.error('(isinstance(self.page_str,str) and len(self.page_str)<50),url:'\
                         +self.cur_url)
           return -1

       this_dic = {}
       title = ''
       meta = {}       
       #os.sys.stdout.buffer.write(pstr.encode('utf-8'))
       bs = BeautifulSoup(self.page_str) 
       if(bs is None) or (bs.head is None) or (bs.head.descendants is None):
           logging.error('(bs is None) or (bs.head is None) or (bs.head.descendants is None).page_str:'\
                         +self.page_str)
           return -1

       metai=0       
       for child in bs.head.descendants:
            #if(not isinstance(child,bs4.element.NavigableString)) or \
            # isinstance(child,bs4.element.Comment) or isinstance(child,bs4.element.Doctype):continue
            #print('------------------------------------------')
            if(type(child) is not bs4.element.Tag):
                continue
            if(child.name in ['script','style','link']):
                continue
            #os.sys.stdout.buffer.write(child.encode('utf-8'))
            #if(child.strip()==''):continue
            if(child.name=='title'):
                title = child.get_text().strip().lower()
                #print('title:'+child.name)
                #print(child)
                continue
            if(child.name=='meta' and child.has_attr('content')):
                if(child.has_attr('name')):
                    meta[child['name'].strip().lower()] = child['content'].strip().lower()
                    #print(child['name'].strip()+':'+child['content'].strip())
                    #print(child)
                    continue
                else:
                    meta[str(metai)] = child['content'].strip().lower()
                    #print(str(metai)+':'+child['content'].strip())
                    metai += 1 
                    #print(child)  
                    continue
       
       this_dic['title'] = title
       this_dic['meta'] = meta
       #logging.info(str(this_dic))
       return this_dic
    

if __name__=='__main__':
    '''
    wf=WebFetch()
    #wf.get_start_domain(url)
    #print(wf.get_links(url))
    #print(wf.header_dict)
    #print(wf.page_str)
    #print(wf.get_all_text(url))
    #os.sys.stdout.buffer.write(wf.get_all_text(url).encode('gb18030'))
    #print(wf.get_title_meta(url))
    '''

    '''
    x=wf.get_page(url)
    wf.page_str=wf.page_str.lstrip('\ufeff')
    print(type(wf.get_all_text()))
    print(wf.get_all_text().encode('UTF-8','ignore').decode('UTF-8','replace'))
    print(wf.header_dict)
    print(wf.header_dict['content-type'].find('text/html'))
   
    x='http://sdfe.com/qwe.aspx?ty=89'
    print(x.rfind('aspx1'))
    print(wf.get_title_meta())
    '''
    
    '''------------download image-----------
    url='http://www.chinanews.com/tp/hd2011/2013/11-07/U86P4T426D262696F16470DT20131107210423.jpg'
    mypath='C:\\Users\\Administrator\\Desktop\\img'
    wf=WebFetch()
    bytes=wf.get_img(url,mypath)
    '''
