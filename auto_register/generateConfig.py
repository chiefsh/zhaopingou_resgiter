import os
import json




class generateConfig(object):


    def __init__(self):
        self.config_dict = {
              "interface_config": {
                "input_server": {
                  "url_template": "http://47.93.240.129:30080/select?user_id={user_id:d}&type=1"
                },
                "rabbitmq": {
                  "username": "spider",
                  "password": "spider",
                  "host": "47.93.240.129",
                  "port": 5672
                },
                "output_queue": {
                  "queue_name": "web-crawler-queue-large",
                  "exchange_name": "spider",
                  "routing_key": "web-crawler-queue-large"
                },
                "company_output_queue": {
                  "queue_name": "web-crawler-queue-company",
                  "exchange_name": "spider",
                  "routing_key": "web-crawler-queue-company"
                }
              },
              "site_list": [
                "zhaopingou"
              ],
              "site_config": {
                "zhaopingou": {
                  "account_list": [

                  ]
                }
              }
}



    def generateConf(self):
        with open('account.txt') as f:
            lines = f.readlines()
            user_id = 1001
            ip = 4
            tag = 0
            count = 0
            for line in lines:
                account = {}
                line = line.strip()
                account['user_id'] = user_id
                account['username'] = line
                account['password'] = 'jianxun1302'
                if tag==0:
                    self.config_dict['site_config']['zhaopingou']['account_list'].append(account)
                    filename = 'config_online_zhaopingou'+str(ip)+"-1.json"
                    with open(filename,'w') as j:
                        json_str = json.dumps(self.config_dict,ensure_ascii=False)
                        j.write(json_str)
                    tag = 1
                    self.config_dict['site_config']['zhaopingou']['account_list']=[]
                    continue
                if tag==1:
                    self.config_dict['interface_config']['input_server'][
                        'url_template'] = "http://47.93.240.129:30080/select?user_id={user_id:d}&type=2"
                    if count<3:
                        self.config_dict['site_config']['zhaopingou']['account_list'].append(account)
                        count+=1
                        continue
                    filename2 = 'config_online_zhaopingou'+str(ip)+"-2.json"
                    with open(filename2,'w') as h:
                        json_str = json.dumps(self.config_dict,ensure_ascii=False)
                        h.write(json_str)
                    self.config_dict['site_config']['zhaopingou']['account_list'] = []
                    self.config_dict['interface_config']['input_server']['url_template'] = "http://47.93.240.129:30080/select?user_id={user_id:d}&type=1"
                    tag=0
                    ip+=1
                    user_id+=1
                    count = 0



if __name__=="__main__":
    g = generateConfig()
    g.generateConf()