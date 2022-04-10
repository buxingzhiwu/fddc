#-*- coding: utf-8 -*-
import subprocess, sys, os, time, socket

# tc:
zjc_dir = os.path.dirname(os.path.abspath(__file__))
group_dir=os.path.dirname(zjc_dir)
code_dir=os.path.dirname(group_dir)
project_dir=os.path.dirname(code_dir)

cmd = 'python '+zjc_dir+'/zjc_part1.py' #tc:把所有python3改成python
res = subprocess.call(cmd.split())  #tc:call可变check_output返回res，用res.decode("utf-8")看输出
print("zjc_part1 finish!!",";zjc_part1.py exit_code:",res)

for i, val in enumerate([(677, "bilstm"), (528, "bilstm"),(115, "idcnn"), (1024, "idcnn")]):
    if not os.path.exists(group_dir+"/InformationExtraction/zjc{0}".format(i + 1)):
        os.mkdir(group_dir+"/InformationExtraction/zjc{0}".format(i + 1))

    cmd = 'python '+zjc_dir+'/zengjianchi.py 0 1 0 {0}'.format(val[0])
    res = subprocess.call(cmd.split())
    print("i:",i,";val:",val,";zengjianchi.py exit_code:",res)

    # cmd = 'cd ./InformationExtraction && python3 main.py' \
    #       ' --model_type \"{2}\"'\
    #       ' --ckpt_path \"zjc{0}\" --log_file \"zjc{0}/train.log\"' \
    #       ' --map_file \"zjc{0}/maps.pkl\" --config_file \"zjc{0}/config_file\"' \
    #       ' --train_file \"./data/zjc.data.train\" ' \
    #       ' --dev_file \"./data/zjc.data.dev\"' \
    #       ' --result_path \"zjc{0}\" --train {1}'.format(i + 1, True, val[1])
    # subprocess.call(cmd, shell=True)

    cmd = 'cd '+group_dir+'/InformationExtraction && python main.py' \
          ' --model_type \"{1}\"' \
          ' --answer_file \"./data/zjc.TEST\"'\
          ' --answer_save \"../zjc/tem/zjc_save{0}.json\"' \
          ' --ckpt_path \"zjc{0}\" --log_file \"zjc{0}/train.log\"' \
          ' --map_file \"zjc{0}/maps.pkl\" --config_file \"zjc{0}/config_file\"'.format(i + 1, val[1])
    res = subprocess.call(cmd, shell=True)
    print("InformationExtraction/main.py exit_code:", res)

cmd = 'python '+zjc_dir+'/zjc_part2.py'
res = subprocess.call(cmd.split())
print("zjc_part2 finish!!,",";zjc_part2.py exit_code:",res)