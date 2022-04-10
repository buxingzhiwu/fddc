#-*- coding: utf-8 -*-
import subprocess, sys, os, time, socket

# tc:
ht_dir = os.path.dirname(os.path.abspath(__file__))
group_dir=os.path.dirname(ht_dir)
code_dir=os.path.dirname(group_dir)
project_dir=os.path.dirname(code_dir)

for i, val in enumerate([(633, "bilstm"), (52668, "bilstm"),(11555, "idcnn"), (1024, "idcnn")]):
    if not os.path.exists(group_dir+"/InformationExtraction/ht{0}".format(i + 1)):
        os.mkdir(group_dir+"/InformationExtraction/ht{0}".format(i + 1))
#
    cmd = 'python '+ht_dir+'\\hetong.py 0 1 {0}'.format(val[0])
    res = subprocess.call(cmd.split())
    print("i:", i, ";val:", val, ";hetong.py exit_code:", res)

    # cmd = 'cd ./InformationExtraction && python3 main.py' \
    #       ' --model_type \"{2}\"'\
    #       ' --ckpt_path \"ht{0}\" --log_file \"ht{0}/train.log\"' \
    #       ' --map_file \"ht{0}/maps.pkl\" --config_file \"ht{0}/config_file\"' \
    #       ' --train_file \"./data/ht.data.train\" ' \
    #       ' --dev_file \"./data/ht.data.dev\"' \
    #       ' --result_path \"ht{0}\" --train {1}'.format(i + 1, True, val[1])
    # subprocess.call(cmd, shell=True)

    cmd = 'cd '+group_dir+'/InformationExtraction && python main.py' \
          ' --model_type \"{1}\"' \
          ' --answer_file \"./data/ht.TEST\"'\
          ' --answer_save \"../ht/tem/ht{0}.json\"' \
          ' --ckpt_path \"ht{0}\" --log_file \"ht{0}/train.log\"' \
          ' --map_file \"ht{0}/maps.pkl\" --config_file \"ht{0}/config_file\"'.format(i + 1, val[1])
    res = subprocess.call(cmd, shell=True)
    print("InformationExtraction/main.py exit_code:", res)

cmd = 'python '+ht_dir+'/zdht_part2.py'
res = subprocess.call(cmd.split())
print("zdht_part2.py exit_code:",res)

cmd = 'python '+ht_dir+'/concat.py'
res = subprocess.call(cmd.split())
print("concat.py exit_code:",res)