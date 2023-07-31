import os
import yaml
import json
from snippets import get_current_time_str

config = yaml.safe_load(open("conf/360_sft_base.yaml"))
print(json.dumps(config, ensure_ascii=False, indent=4))


cur_day = get_current_time_str("%m%d")
cur_min = get_current_time_str("%H%M")
cur_daymin = get_current_time_str("%m%d%H%M")


do_run = True
envs = {
    "ENV_LR": "1.0e-5",
    "ENV_CKPT_SAVE_INTERVAL": 150,
    "ENV_RAW_DATASET_PATH": "/data/rawdataset/360sft_30k_v2.jsonl",
    "ENV_EVAL_INTERVAL": 150,
    "ENV_MIN_LOSS_SCALE": 0.01,
    "ENV_NUM_WORKERS": 8,
    "ENV_TRAIN_TOKENS": 76800000,
    "ENV_GLOBAL_BATCH_SIZE": 128
}
basemodel = "/home/bmm-system/data/system/models/glm-130b-pretrain"
basemodel = "/data/glusterfs/chenhao/experiment/360-sft-130b-07261541/ckpts"


# set name and namespace
job_name = f"chenhao-360-sft-130b-{cur_daymin}"
namespace = "research"

config["metadata"]["name"] = job_name
config["metadata"]["namespace"] = namespace

# set volume and env


path_dict = dict(
    basemodel=(basemodel, "Directory", ("main", "worker")),
    rawdataset=("/data/glusterfs/chenhao/workspace/sft/data/360",
                "Directory", ("main")),
    project=("/data/glusterfs/chenhao/workspace/bmm-ft-chatglm-130b",
             "Directory", ("main", "worker")),
    output=(
        f"/data/glusterfs/chenhao/experiment/360-sft-130b-{cur_daymin}", "DirectoryOrCreate", ("main", "worker", "agent"))
)

mount_dict = dict(
    dshm="/dev/shm",
    basemodel="/data/basemodel",
    rawdataset="/data/rawdataset",
    output="/data/output",
    project="data/project"
)

args = ["--hostenvs",
        "VC_MAIN_HOSTS",
        "VC_WORKER_HOSTS"]
if do_run:
    # args.extend(["--commands", "cd /data/project", "sh scripts/sft.sh"])
    args.extend(
        ["--commands", "python3 data/process_sft.py --data_path ${ENV_RAW_DATASET_PATH} --output_dir ${ENV_INPUT_DATASET_PATH}/train", "bash scripts/submit_gpu.sh configs/glm-130b/glm-130b-sft.sh"])


image = 'a100-harbor.bigmodel.cn/maas/bmm-chatglm-130b:train-20230720175103'


for task in config["spec"]["tasks"]:
    # set volume
    task_name = task["name"]
    print(f" processing {task_name}")
    volumes = task["template"]["spec"]["volumes"]

    for k, (path, _type, names) in path_dict.items():
        if task_name not in names:
            continue
        volumes.append(
            {"name": k, "hostPath": {"path": path,  "type": _type}})

    # set volumnMount
    container = task["template"]["spec"]["containers"][0]

    if task_name == "main":
        container["args"] = args

    container["volumeMounts"] = [
        {"name": k, "mountPath": v} for k, v in mount_dict.items()
        if k in path_dict and task_name in path_dict[k][2]]
    # set env
    container["image"] = image
    origin_env = {item["name"]: item["value"] for item in container["env"]}
    origin_env.update(**envs)
    container["env"] = [{"name": key, "value": str(
        value)} for key, value in origin_env.items()]

print(json.dumps(config, ensure_ascii=False, indent=4))


tgt_path = f"conf/360sft/{cur_day}/{cur_min}.yaml"
if not os.path.exists(os.path.dirname(tgt_path)):
    os.makedirs(os.path.dirname(tgt_path))

print(f"dump config to {tgt_path}")
yaml.dump(config, open(tgt_path, "w"))
