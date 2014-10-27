import codecs
import logging
import os

def initlog (file_name=""):
    this_file_name = file_name + '_log.log'
    '''if not os.access(this_file_name,os.F_OK):
        fd=os.open(this_file_name,os.O_RDWR|os.O_APPEND|os.O_CREAT)
        os.close(fd)
    '''
    f = codecs.open(this_file_name,mode='a',encoding='utf-8')
    #logging.basicConfig(format='%(asctime)s:%(pathname)s:%(lineno)d:%(levelname)s:%(message)s',\
    #filename=this_file_name,level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s:%(pathname)s:%(lineno)d:%(levelname)s:%(message)s\r\n',\
    stream=f,level=logging.DEBUG)


if __name__=="__main__":
   initlog('b');
   logging.error("this is my first log!")
   logging.info("this is my first log!")
