# coding=utf-8
import os
from modelscope.utils.hub import read_config, snapshot_download
from modelscope.metainfo import Trainers
from modelscope.trainers import build_trainer

def main():
    # 工作目录设置
    work_dir = "wake_up/tmp"  # 训练过程文件保存路径
    
    # 步骤1：获取基础模型
    base_model_id = "speech_charctc_kws_phone-xiaoyun"  # 基础模型ID
    # model_dir = snapshot_download(base_model_id)  # 下载模型
    
    # 步骤2：配置训练参数
    configs = read_config(base_model_id)
    # 调整训练参数（根据需求修改）
    configs.train.max_epochs = 10          # 增加训练轮次
    configs.preprocessor.batch_conf.batch_size = 5  # 调整批次大小
    configs.train.optimizer.lr = 0.0001    # 设置学习率
    configs.train.dataloader.workers_per_gpu = 8  # 数据加载线程数

    # 保存修改后的配置文件
    config_file = os.path.join(work_dir, "finetune_config.json")
    configs.dump(config_file)

    # 步骤3：创建训练器
    trainer_args = {
        "model": base_model_id,
        "work_dir": work_dir,
        "cfg_file": config_file,
        "seed": 2023  # 随机种子
    }
    trainer = build_trainer(
        Trainers.speech_kws_fsmn_char_ctc_nearfield,
        default_args=trainer_args
    )

    # 步骤4：准备微调数据（需要提前准备好）
    train_scp = "wake_up/train_wav.scp"  # 训练数据列表
    cv_scp = "wake_up/cv_wav.scp"       # 验证数据列表
    trans_file = "wake_up/merge_trans.txt"  # 标注文件
    
    # 步骤5：启动微调训练
    train_kwargs = {
        "train_data": train_scp,
        "cv_data": cv_scp,
        "trans_data": trans_file,
        "checkpoint": "",  # 继续训练时可指定已有checkpoint
        "tensorboard_dir": os.path.join(work_dir, "tensorboard"),
        "need_dump": True   # 保存中间模型
    }
    trainer.train(**train_kwargs)

    # 步骤6：模型评估（需要测试数据）
    if int(os.environ.get("RANK", 0)) == 0:  # 主进程执行评估
        test_scp = "wake_up/cv_wav.scp"
        keywords = "莉可"  # 修改为自定义唤醒词，多个用逗号分隔
        
        test_kwargs = {
            "test_dir": os.path.join(work_dir, "evaluation"),
            "test_data": test_scp,
            "trans_data": trans_file,
            "keywords": keywords,
            "average_num": 5,    # 使用最好的5个checkpoint平均
            "batch_size": 128
        }
        trainer.evaluate(None, **test_kwargs)  # 自动选择最佳checkpoint

if __name__ == "__main__":
    main()