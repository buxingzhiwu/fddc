#!/usr/bin/env python
# -*- coding:utf-8 -*-

#tc:额外编写训练启动文件

import subprocess, sys, os, time, socket

zjc_dir = os.path.dirname(os.path.abspath(__file__))
group_dir=os.path.dirname(zjc_dir)
code_dir=os.path.dirname(group_dir)
project_dir=os.path.dirname(code_dir)

for i, val in enumerate([(677, "bilstm"), (528, "bilstm"),(115, "idcnn"), (1024, "idcnn")]):
    if not os.path.exists(group_dir+"/InformationExtraction/zjc{0}".format(i + 1)):
        os.mkdir(group_dir+"/InformationExtraction/zjc{0}".format(i + 1))

    cmd = 'python ' + zjc_dir + '/zengjianchi.py 1 0 0 {0}'.format(val[0])
    res = subprocess.call(cmd.split())
    print("i:", i, ";val:", val, ";zengjianchi.py exit_code:", res)

    cmd = 'cd '+group_dir+'/InformationExtraction && python main.py' \
          ' --model_type \"{1}\"' \
          ' --ckpt_path \"zjc{0}\" --log_file \"zjc{0}/train.log\"' \
          ' --map_file \"zjc{0}/maps.pkl\" --config_file \"zjc{0}/config_file\"' \
          ' --train_file \"./data/zjc.data.train\" ' \
          ' --dev_file \"./data/zjc.data.dev\"' \
          ' --result_path \"zjc{0}\" --train {2}'.format(i + 1,val[1], True)
    res = subprocess.call(cmd, shell=True)
    print("InformationExtraction/main.py exit_code:", res)