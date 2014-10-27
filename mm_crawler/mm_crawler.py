#!/usr/bin/python3

import os
from bs4      import BeautifulSoup
from bs4      import * 
import bs4
import sys
import time
from traceback import  *
import re
from queue import *
import threading
from mylog import *
from WebFetch import WebFetch
import getopt


class MMCrawler:
    
    def __init__ (self):
        
        self.filter_dict = {
         '.mpg':1,'.avi':1,'.rmvb':1,'.rm':1,'.swf':1,'.flv':1,'.rar':1,'.mkv':1,'.mpeg':1,'.mp4':1,
         '.wma':1,'.wmv':1,'.mp3':1,'.js':1,'.gzip':1,'.cab':1,'.jar':1,'.sis':1,'.css':1,'.wbmp':1,
         '.tiff':1,'.tif':1,'.pdf':1
        }

        self.filter_dict1 = {'.html':1,'.htm':1}
        self.filter_keyword = ['/images/','/attachment/flink/']
 
        self.wf = WebFetch()
        self.domain = None

        #url_dict:{'url':0,'url':1}
        self.url_dict = {}
        self.url_dict_lock = threading.Lock()
        self.url_queue = Queue(1000)
        self.img_url_dict = {}
        self.img_count = 0
        self.img_count_lock = threading.Lock()
        self.get_img_continue = True
        self.crawl_finished = False

    '''
    '''
    def img_url_filter(self,url):
        if(not isinstance(url,str)):
            logging.error('Not isinstance(url,str),url:'+url) 
            return False
        for tmp_key in self.filter_keyword :
            ret = url.rfind(tmp_key)
            if(ret != -1):
                logging.error('(tmp_key.rfind(tmp_key)!=-1),ret:'\
                              +str(ret)+' tmp_key:'+tmp_key+' url:'+url) 
                return True
        return False
        
    def crawl_url_filter (self,url):
        if(not isinstance(url,str)):
            logging.error('Not isinstance(url,str),url:'+url) 
            return False
            
        if(url[url.rfind("."):] not in self.filter_dict): 
            return False
        else:
            return True
            

    def crawl_thread(self,pic_dir='./pics',img_count_limit=None):
        thread_name = threading.current_thread().name
        print('Thread '+thread_name+' started!')
        if(not pic_dir.endswith("/")):
            pic_dir += '/'
        
        while (not self.crawl_finished):
            while self.get_img_continue and (not self.crawl_finished):
                try:
                  tmp_url = self.url_queue.get(False)
                except Empty:
                    time.sleep(0.1)
                else:
                    break
            else:
                print(thread_name+' finished,img_count:'+str(self.img_count))
                return
                
            print(thread_name+' New url:'+tmp_url\
                  +' qsize:'+str(self.url_queue.qsize()))
            self.url_dict_lock.acquire()
            self.url_dict[tmp_url] = 1
            self.url_dict_lock.release()

            if(self.crawl_url_filter(tmp_url)):
                #print('Filtered:'+k)
                logging.info(thread_name+' Filtered url:'+tmp_url)
                continue

            tmp_url_dict = self.wf.get_links(tmp_url)
            time.sleep(1)
            #print(type(url_dict))
            if(not isinstance(tmp_url_dict,dict)):
                 logging.error(thread_name+' Get links error,url:'+tmp_url)
                 continue
            #print(url_dict)       
            #print(wf.header_dict)
            find_ret = self.wf.header_dict['content-type'].find('text/html')
            #print('Url:'+tmp_url+' content-type:'+self.wf.header_dict['content-type'])
            #logging.info('Url:'+tmp_url+' content-type:'+self.wf.header_dict['content-type'])
            #check from headers
            if(find_ret==-1):
                #print('Not text/html,url:'+tmp_url)
                logging.error(thread_name+' Not text/html,url:'+tmp_url)
                continue
            #check from url tail,Get htm and html text
            #self.ar_filter(tmp_url)

            d_len = len(tmp_url_dict)
            for tmp_key,tmp_value in tmp_url_dict.items():
                
                if(self.url_dict.get(tmp_key) is not None):
                    continue
                else:
                    start_domain = self.wf.get_start_domain1(tmp_key)
                    if(start_domain!=self.wf.domain) or self.crawl_url_filter(tmp_key):
                        logging.error(thread_name+' start_domain:['+ start_domain+\
                                      '] domain:['+self.wf.domain+\
                                      '] Filter or external link:'+tmp_key)
                        self.url_dict[tmp_key] = 1
                        continue
                    self.url_dict_lock.acquire()
                    self.url_dict[tmp_key] = 0
                    self.url_dict_lock.release()
                #write_count+=1
           
            tmp_img_dict = self.wf.get_img_links(tmp_url)
            time.sleep(1)
            if(tmp_img_dict is None):
                logging.error(thread_name+' Can\'t find image, url:'+tmp_url)
                continue
            for tmp_key,tmp_value in tmp_img_dict.items():
                if(self.img_url_dict.get(tmp_key) is not None):
                    continue
                else:
                    self.img_url_dict[tmp_key] = 1
                    print(thread_name+' IMG:'+tmp_key+\
                         ' qsize:'+str(self.url_queue.qsize()))
                    logging.info(thread_name+' IMG:'+tmp_key+\
                         ' qsize:'+str(self.url_queue.qsize()))
                    
                    if(self.img_url_filter(tmp_key)):
                        logging.info('Filtered img url:'+str(tmp_key))
                        continue
                        
                    self.img_count_lock.acquire()
                    if(not self.get_img_continue):
                        print(thread_name+' finished,img_count:'+str(self.img_count))
                        self.img_count_lock.release()
                        return 
                    
                    ret=self.wf.get_img(tmp_key,pic_dir)
                    time.sleep(1)
                    if(isinstance(ret,int)):
                        logging.error(thread_name+'get_img error,url:'\
                                      +str(tmp_key)+' qsize:'+str(self.url_queue.qsize()))
                    else:
                        self.img_count +=1
                        if(img_count_limit is not None) and \
                          (self.img_count>=img_count_limit):
                            self.get_img_continue = False
                            self.img_count_lock.release()
                            print(thread_name+' finished,img_count:'+str(self.img_count))
                            return
                    self.img_count_lock.release()
                            
        print(thread_name+' finished,img_count:'+str(self.img_count))
        

    def get_url_thread (self):
        thread_name = threading.current_thread().name
        print('Thread '+thread_name+' started!')
        total_url_count = 0
        time_zero_count = 0
        while not self.crawl_finished:
            tmp_url_list=[]
            url_count = 0
            self.url_dict_lock.acquire()
            for k,v in self.url_dict.items():
                if(v==0):
                    start_domain = self.wf.get_start_domain1(k)
                    if(start_domain!=self.wf.domain):
                        logging.error(thread_name+' start_domain:'+ start_domain+\
                                      ' domain:'+self.wf.domain+' External link:'+tmp_key)
                        self.url_dict[k] = 1
                        continue
                    tmp_url_list.append(k)
                    total_url_count += 1
                    url_count += 1
            self.url_dict_lock.release()
            
            for tmp_url in tmp_url_list:
                while(self.get_img_continue):
                    try:
                        self.url_queue.put(tmp_url,False)
                    except Full:
                        time.sleep(1)
                    else:
                        break
                else:
                    print('Thread '+thread_name+' finished!')
                    return 
            if(url_count>0):
                print('Total url count:'+str(total_url_count)+\
                      ' added url count:'+str(url_count))
                time_zero_count = 0
            else:
                time_zero_count += 1
                
            if(time_zero_count>20) and (url_count==0):
                self.crawl_finished = True
                
            time.sleep(1)
        print('Thread '+thread_name+' finished. crawl_finished:'+str(self.crawl_finished))
        
def usage():
    print('mm_crawler.py usage:')
    print('-h,--help: print help message.')
    print('-n <number>: Specify the number of worker threads,default 10.')
    print('-o <dir>: Saving the picture to <dir>,default ./pics.')
    print('-l <number>: Set the total picture downloaded, default no limit.')
    

# file: WebFetch.py,mylog.py
if __name__=='__main__':
    
    crawl_img_limit = None
    thread_limit = 10
    pic_dir='./pics'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:o:l:", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit()
    output = None
    verbose = False
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit()
        elif o in ("-n"):
            print(o,a)
            thread_limit = int(a)
        elif o in ("-o"):
            print(o,a)
            pic_dir = a
        elif o in ("-l"):
            print(o,a)
            crawl_img_limit = int(a)
        else:
            assert False, "unhandled option"
    
    #print('thread_limit:'+str(thread_limit))
    #print('pic_dir:'+pic_dir)
    #print('crawl_img_limit:'+str(crawl_img_limit))
    #sys.exit(1)
    
    initlog('mm_crawler')
    
    start_url='http://www.22mm.cc'
    start_url='http://www.nipic.com'
    
    if(not os.access(pic_dir,os.F_OK)):
        os.mkdir(pic_dir)
        logging.info('Make picture dir:'+pic_dir)
    
    
    mm_crawler = MMCrawler()
    mm_crawler.url_queue.put(start_url)
    
    url_thread = threading.Thread(target=mm_crawler.get_url_thread,name='get_url')
    url_thread.start()
    time.sleep(0.1)
    
    crawl_threads_list = []
    for i in range(1,thread_limit+1): 
        tmp_thread = threading.Thread(target=mm_crawler.crawl_thread,\
                                      name='crawl_thread_'+str(i),args=(pic_dir,crawl_img_limit))
        crawl_threads_list.append(tmp_thread)
        tmp_thread.start()
        time.sleep(0.1)
         
    url_thread.join()
    for tmp_thread in crawl_threads_list:
        tmp_thread.join()
        
    print('Main thread finished,download img count:'+str(mm_crawler.img_count))


