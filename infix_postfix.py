#!/usr/bin/python3
# 中缀表达式转换为后缀表达式及单元测试

import os
import unittest

# http://www.nowamagic.net/librarys/veda/detail/2307
operator_precedence = {
    '+':1,
    '-':1,
    '*':2,
    '/':2,
    '^':3,
    '%':3
}

operator_list = ['+','-','*','/','^','%','(',')']

def is_valid (char):
    if(len(char)!=1):
        return False
    #print('char:'+char)
    if ((char<='9') and (char >='0')) \
       or (char in operator_list):
        return True
    else:
        return False

def get_level (op):
    ret=operator_precedence.get(op)
    if(ret is not None):
        return operator_precedence[op]
    else:
        return 0


#[+,*
# 100+(-220+302)*48  ==> 100,-220,302,+,-,48,*,+
def get_exp_list (exp):
    #print(exp)
    exp_list = []
    exp_len = len(exp)
    i = 0
    single=''
    while i<exp_len:
        if(not is_valid(exp[i])):
            return None
        #print(exp[i])
        elif(i==0) and (exp[i]=='-'):
            single += exp[i]
        elif(i>0) and (exp[i-1]=='(') and (exp[i]=='-'):
            single += exp[i]
        elif(exp[i]>='0' and exp[i]<='9'):
           single += exp[i]
        else:
            if(single!=''):
                exp_list.append(single)
            single=''
            exp_list.append(exp[i])
        i+=1
    exp_list.append(single)
    return exp_list

def  convert(exp_list):
     out_put_list=[]
     op_stack=[]

     for tmp in exp_list:
         if(tmp.lstrip('-').isnumeric()):
             out_put_list.append(tmp)
         elif(tmp=='('):
             op_stack.append(tmp)
         elif(tmp==')'):
             tmp_op=op_stack.pop()
             while(tmp_op!='('):
                 out_put_list.append(tmp_op)
                 tmp_op=op_stack.pop()
         elif op_stack:
             cur_level = get_level(tmp)
             tmp_op = op_stack[len(op_stack)-1]
             last_level = get_level(tmp_op)
             if(tmp_op == '('):
                 op_stack.append(tmp)
                 continue
             #print('cur_level:'+str(cur_level)+' last_level:'\
             #     +str(last_level)+' tmp_op:'+tmp_op+' tmp:'+tmp+' '+str(op_stack))
             while(last_level>=cur_level) and op_stack:
                 tmp_op = op_stack.pop()
                 out_put_list.append(tmp_op)
                 if(op_stack):
                     tmp_op = op_stack[len(op_stack)-1]
                     if(tmp_op == '('):
                         op_stack.append(tmp)
                         break
                     last_level = get_level(tmp_op)
                     #print('cur_level:'+str(cur_level)+' last_level:'\
                     #     +str(last_level)+' tmp_op:'+tmp_op+' tmp:'+tmp+' '+str(op_stack))
                 else:
                     break
             op_stack.append(tmp)
         else:
             op_stack.append(tmp)

     while op_stack:
         out_put_list.append(op_stack.pop())
     #print(out_put_list)       
     return out_put_list
     
def infix_postfix (exp):
    exp_list = get_exp_list(exp)
    if(exp_list is None):
        return None
    return convert(exp_list)
    

class Test_infix_postfix(unittest.TestCase):
    def setUp(self):
        pass 
        
    def test_correctness (self):
        self.assertEqual(infix_postfix('9+(3-1)*3+10/2'),\
                         ['9', '3', '1', '-', '3', '*', '+', '10', '2', '/', '+'])
        self.assertEqual(infix_postfix('100+(-220+302)*48'),\
                         ['100', '-220', '302', '+', '48', '*','+'])
        
    def test_error_char (self):
        self.assertEqual(infix_postfix('abc'),None)
        
# test command : 
# python -m unittest infix_postfix.Test_infix_postfix
# 
if __name__=='__main__':

    exp = '100+(-220+302)*48'
    exp = '9+(3-1)*3+10/2'
    #exp='abcdfrg'
    print(exp)
    print(infix_postfix(exp))
    

   


    
