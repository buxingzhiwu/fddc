#-*- coding: utf-8 -*-

import os
# ht_dir = os.path.dirname(os.path.abspath(__file__))
# group_dir=os.path.dirname(ht_dir)
# code_dir=os.path.dirname(group_dir)
# project_dir=os.path.dirname(code_dir)
# data_path=project_dir+'\\data'

# html文件路径
# path_train = "/FDDC_announcements_round1_train_20180518/重大合同/"
# # path_test =  data_path+"/FDDC_announcements_round1_test_b_20180708/重大合同/html/"
# path_test =  "D:\study\grade4\Graduation_design\code\\flask\data\ht\\"
# # 提取的数据保存地址
# save_path = "D:\study\grade4\Graduation_design\code\\flask\modelfile\ht\\tem\\"
# #
# save_crope_path = "D:\study\grade4\Graduation_design\code\\flask\modelfile\InformationExtraction\data\\"
# #
# save_fin ="D:\study\grade4\Graduation_design\code\\flask\modelfile\submit\\"


path_test = os.path.dirname(os.path.abspath(__file__))+'\\'+ "../../data/"
# 提取的数据保存地址
save_path = os.path.dirname(os.path.abspath(__file__))+'\\'+ "../ht/tem/"
#
save_crope_path = os.path.dirname(os.path.abspath(__file__))+'\\'+ "../InformationExtraction/data/"
#
save_fin =os.path.dirname(os.path.abspath(__file__))+'\\'+ "../submit/"
