#!/usr/bin/python3

from urllib.parse import urlparse

class DomainSuffix:
    def __init__ (self):
        self.ds = dict()
        self.file_name = ''
        self.is_load = False
    '''
    return value: -1 for error. 1 for success.
    '''
    def load_file (self,filename):
        if(len(filename)<1): 
            return -1
        self.file_name = filename
        try: 
            f = open(filename,"rb+")
        except: 
            return -1
        s = f.readlines()
        #os.sys.stdout.buffer.write(s)
        for si in s:
          tmp_str = si.decode('utf-8')
          tmp_s1 = tmp_str.split(":")
          if(tmp_s1[0].startswith(".") and len(tmp_s1)==2):
              self.ds[tmp_s1[0]] = 1
        #print(self.ds.get(0))
        f.close()
        self.is_load = True
        return 1
    '''
    return value: -1 for error, top level domain string for success.
    '''
    def get_top_domain (self,url):
        if(not isinstance(url,str)) or  url.startswith("/") or \
          (not url.startswith('http://')) or not self.is_load: 
            return -1        
       
        tmp_lower_url=url.lower()
        #urlparse Parse a URL into six components, returning a 6-tuple.
        #example: o = urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
        #ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html',
        #params='', query='', fragment='') 
        tmp_domain_p = urlparse(url)
        tmp_domain = tmp_domain_p[1].rstrip('0123456789:')
        #Return a list of the words in the string        
        domain_item = tmp_domain.split('.')
        if(len(domain_item)<2):
            print('Error:'+str((len(tmp_domain)<2))+'url:'+url)
            return -1
        #print(domain_item)
        domain_item.reverse()
        #print(domain_item)
        type=0
        suffix2 = '.' + domain_item[1] + '.' + domain_item[0]
        suffix1 = '.' + domain_item[0]
        if(self.ds.get(suffix2)):
            #print('Found:'+suffix2+':'+str(self.ds.get(suffix2)))
            type=2
        elif(self.ds.get(suffix1)):
            #print('Found:'+suffix1+':'+str(self.ds.get(suffix1)))
            type=1
        else:
            #print('Can\'t found')
            return -1

        if(type==1):
            domain = domain_item[1]+suffix1
        elif(type==2):
            domain = domain_item[2]+suffix2
        else:
            return -1
        #print('domain['+domain+']')
        return domain        

if __name__=="__main__":
    #os.sys.stdout.buffer.write(x)
    ds = DomainSuffix()
    load_ret = ds.load_file('./domain_suffixes.txt')
    print(ds.ds)
    print('load_ret:'+str(load_ret))
    url = "http://www.phpchina.com/archives/view-42584-1.html"
    domain = ds.get_top_domain(url)
    print('Final,domain['+domain+']')
