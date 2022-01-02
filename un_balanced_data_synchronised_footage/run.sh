#!/usr/bin/env bash

export PATH=/home/rdai/anaconda3/envs/torch1.9/bin:$PATH

python train.py \
-dataset TSU \
-mode rgb \
-model TCN \
-train True \
-num_channel 512 \
-lr 0.0002 \
-kernelsize 3 \
-comp_info TSU_TCN \
-APtype map \
-epoch 140 \
-batch_size 2 \
-dataset_path unbalanced_data_synchronised_footage.json\
-num_classes 51 \
-rgb_root - #change here



#This shell script is used to run the model.


#Arguments Description.



: '

 1).The first argument speicifies which train file has to be run for example.. for joint view we run train_joint_view.py and accordingly for each type of model theres a corresponding train file that has to be run. the train files are     in train folder.

 2). dataset_path - This argument is used to speicfy the path to the datasets. Note - Make sure to use the appropriate dataset for specific task as mentioned in readme

 3). rgb_root - This argument is used to specify the path to the features extracted from the videos. In our case we used a pretrained I3D model to extract features.

Note - plase make sure to change the argumnets accordingly before running.

'



