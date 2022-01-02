





##########################-The code is modified to train on joint view action detetcion -##################


from __future__ import division
import time
import os
import argparse
import sys

# import torchvision.models as models
import torch

# sys.path.append('/data/stars/user/rdai/PhD_work/Graph_net')


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser()
parser.add_argument('-mode', type=str, help='rgb or flow (or joint for eval)')
parser.add_argument('-train', type=str2bool, default='True', help='train or eval')
parser.add_argument('-comp_info', type=str)
parser.add_argument('-rgb_model_file', type=str)
parser.add_argument('-flow_model_file', type=str)
parser.add_argument('-gpu', type=str, default='4')
parser.add_argument('-dataset', type=str, default='charades')
parser.add_argument('-rgb_root', type=str, default='no_root')
parser.add_argument('-flow_root', type=str, default='no_root')
parser.add_argument('-type', type=str, default='original')
parser.add_argument('-lr', type=str, default='0.1')
parser.add_argument('-epoch', type=str, default='50')
parser.add_argument('-model', type=str, default='')
parser.add_argument('-APtype', type=str, default='wap')
parser.add_argument('-randomseed', type=str, default='False')
parser.add_argument('-load_model', type=str, default='False')
parser.add_argument('-num_channel', type=str, default='False')
parser.add_argument('-batch_size', type=str, default='False')
parser.add_argument('-kernelsize', type=str, default='False')
parser.add_argument('-feat', type=str, default='False')
arser.add_argument('-num_classes', type=str, default='False')
parser.add_argument('-dataset_path', type=str, default='False')
args = parser.parse_args()

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import random

# set random seed
if args.randomseed=="False":
    SEED = 0
elif args.randomseed=="True":
    SEED = random.randint(1, 100000)
else:
    SEED = int(args.randomseed)

torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.manual_seed(SEED)
np.random.seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
print('Random_SEED!!!:', SEED)

from torch.optim import lr_scheduler
from torch.autograd import Variable

import json

import pickle
import math



if str(args.APtype) == 'wap':
    pass
    #from wapmeter import APMeter
elif str(args.APtype) == 'map':
    from apmeter import APMeter


batch_size = int(args.batch_size)

if args.dataset == 'TSU':
    from smarthome_i3d_per_video_joint_view import MultiThumos as Dataset
    from smarthome_i3d_per_video_joint_view import mt_collate_fn as collate_fn
    train_split = args.dataset_path
    test_split =  args.dataset_path
    classes= int(args.num_classes)
    rgb_root = args.rgb_root


if args.dataset == 'charades':
    from charades_i3d_per_video import MultiThumos as Dataset
    from charades_i3d_per_video import mt_collate_fn as collate_fn
    if args.run_mode == 'debug':
        print('debug!!!')
        train_split = './data/charades_test.json'
        test_split = '/data/stars/user/rdai/PhD_work/CVPR2021_match/data/charades_test.json'
    else:
        train_split = './data/charades.json'
        test_split = './charades.json'
    # print('load feature from:', args.rgb_root)
    rgb_root = '/Path/to/charades_feat_rgb'
    skeleton_root = '/Path/to/charades_feat_pose'
    flow_root = '/Path/to/charades_feat_flow'
    rgb_of=[rgb_root,flow_root]
    classes = 157



def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def load_data_rgb_skeleton(train_split, val_split, root_skeleton, root_rgb):
    # Load Data
    if len(train_split) > 0:
        dataset = Dataset(train_split, 'training', root_skeleton, root_rgb, batch_size, classes)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0,
                                                 pin_memory=True, collate_fn=collate_fn) # 8
    else:

        dataset = None
        dataloader = None

    val_dataset = Dataset(val_split, 'testing', root_skeleton, root_rgb, batch_size, classes)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=1, shuffle=True, num_workers=0,
                                                 pin_memory=True, collate_fn=collate_fn) #2

    dataloaders = {'train': dataloader, 'val': val_dataloader}
    datasets = {'train': dataset, 'val': val_dataset}
    return dataloaders, datasets


def load_data(train_split, val_split, root):
    # Load Data
    if len(train_split) > 0:
        if str(args.feat) == '2d':
            dataset = Dataset(train_split, 'training', root, batch_size, classes, int(args.pool_step))
        else:
            dataset = Dataset(train_split, 'training', root, batch_size, classes)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=8,
                                                 pin_memory=True, collate_fn=collate_fn)
        dataloader.root = root
    else:

        dataset = None
        dataloader = None

    if str(args.feat) == '2d':
        val_dataset = Dataset(val_split, 'testing', root, batch_size, classes, int(args.pool_step))
    else:
        val_dataset = Dataset(val_split, 'testing', root, batch_size, classes)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=1, shuffle=True, num_workers=2,
                                                 pin_memory=True, collate_fn=collate_fn)
    val_dataloader.root = root

    dataloaders = {'train': dataloader, 'val': val_dataloader}
    datasets = {'train': dataset, 'val': val_dataset}
    return dataloaders, datasets


# train the model
def run(models, criterion, num_epochs=50):
    since = time.time()

    best_loss = 10000
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        probs = []
        for model, gpu, dataloader, optimizer, sched, model_file in models:
            train_map, train_loss = train_step(model, gpu, optimizer, dataloader['train'], epoch)
            prob_val, val_loss, val_map = val_step(model, gpu, dataloader['val'], epoch)
            probs.append(prob_val)
            sched.step(val_loss)



def eval_model(model, dataloader, baseline=False):
    results = {}
    for data in dataloader:
        other = data[3]
        outputs, loss, probs, _ = run_network(model, data, 0, baseline)
        fps = outputs.size()[1] / other[1][0]

        results[other[0][0]] = (outputs.data.cpu().numpy()[0], probs.data.cpu().numpy()[0], data[2].numpy()[0], fps)
    return results


def run_network(model, data, gpu, epoch=0, baseline=False):
    
    #taking the models 
    
    model_1 = model[0]
    model_2 = model[1]
    inputs_1, inputs_2, mask,labels,other = data
    #print(other[0], other[1])
    # wrap them in Variable
    inputs_1 = Variable(inputs_1.cuda(gpu))
    inputs_2 = Variable(inputs_2.cuda(gpu))
    mask = Variable(mask.cuda(gpu))
    labels = Variable(labels.cuda(gpu))

    mask_list = torch.sum(mask, 1)
    mask_new = np.zeros((mask.size()[0], classes, mask.size()[1]))
    for i in range(mask.size()[0]):
        mask_new[i, :, :int(mask_list[i])] = np.ones((classes, int(mask_list[i])))
    mask_new = torch.from_numpy(mask_new).float()
    mask_new = Variable(mask_new.cuda(gpu))

    inputs_1 = inputs_1.squeeze(3).squeeze(3)
    inputs_2 = inputs_2.squeeze(3).squeeze(3)
    activation_1 = model_1(inputs_1, mask_new)
    activation_2 = model_2(inputs_2, mask_new)
    #print("output_shape", activation_1.shape, activation_2.shape)
 

    
    outputs_final_1 = activation_1
    outputs_final_2 = activation_2

    outputs_final_1 = outputs_final_1.permute(0, 2, 1)  
    outputs_final_2 = outputs_final_2.permute(0, 2, 1)  
    probs_f_1 = F.sigmoid(outputs_final_1) * mask.unsqueeze(2)
    probs_f_2 = F.sigmoid(outputs_final_2) * mask.unsqueeze(2)
    probs_final = probs_f_1 + probs_f_2
    loss_f_1 = F.binary_cross_entropy_with_logits(outputs_final_1, labels, size_average=False)
    loss_f_2 = F.binary_cross_entropy_with_logits(outputs_final_2, labels, size_average=False)
    
    loss_f_1 = torch.sum(loss_f_1) / torch.sum(mask)  
    loss_f_2 = torch.sum(loss_f_2) / torch.sum(mask)  

    loss = loss_f_1 + loss_f_2 

    corr = torch.sum(mask)
    tot = torch.sum(mask)

    return outputs_final_1,outputs_final_2,loss, probs_final,corr / tot


def train_step(model, gpu, optimizer, dataloader, epoch):
    model[0].train(True)
    model[1].train(True)
    tot_loss = 0.0
    error = 0.0
    num_iter = 0.
    apm = APMeter()
    for data in dataloader:
        
        optimizer.zero_grad()
        num_iter += 1

        outputs_1, outputs_2,loss, probs,err = run_network(model, data, gpu, epoch)
        
        
        
        apm.add(probs.data.cpu().numpy()[0], data[3].numpy()[0])
        error += err.data
        tot_loss += loss.data

        loss.backward()
        optimizer.step()
    if args.APtype == 'wap':
        train_map = 100 * apm.value()
    else:
        train_map = 100 * apm.value().mean()
    print('train-map:', train_map)
    apm.reset()

    epoch_loss = tot_loss / num_iter

    return train_map, epoch_loss


def val_step(model, gpu, dataloader, epoch):
    model[0].train(False)
    model[1].train(False)
    apm = APMeter()
    tot_loss = 0.0
    error = 0.0
    num_iter = 0.
    num_preds = 0

    full_probs = {}

    # Iterate over data.
    for data in dataloader:
        num_iter += 1
        other = data[3]

        outputs_1, outputs_2,loss, probs,err = run_network(model, data, gpu, epoch)

        apm.add(probs.data.cpu().numpy()[0], data[3].numpy()[0])

        error += err.data
        tot_loss += loss.data

        probs = probs.squeeze()

        full_probs[other[0][0]] = probs.data.cpu().numpy().T

    epoch_loss = tot_loss / num_iter


    val_map = torch.sum(100 * apm.value()) / torch.nonzero(100 * apm.value()).size()[0]
    print('val-map:', val_map)
    print(100 * apm.value())
    apm.reset()

    return full_probs, epoch_loss, val_map


if __name__ == '__main__':
    print(str(args.model))
    print('batch_size:', batch_size)
    print('cuda_avail', torch.cuda.is_available())

    if args.mode == 'flow':
        print('flow mode', flow_root)
        dataloaders, datasets = load_data(train_split, test_split, flow_root)
    elif args.mode == 'skeleton':
        print('Pose mode', skeleton_root)
        dataloaders, datasets = load_data(train_split, test_split, skeleton_root)
    elif args.mode == 'rgb':
        print('RGB mode', rgb_root)
        dataloaders, datasets = load_data(train_split, test_split, rgb_root)

    if args.train:
        num_channel = args.num_channel
        if args.mode == 'skeleton':
            input_channnel = 256
        else:
            input_channnel = 1024

        num_classes = classes
        mid_channel=int(args.num_channel)


        if args.model=="TCN":
            print("you are processing PDAN")
            from models_PDAN import Dilated_TCN as Net
            rgb_model_1 = Net(mid_channel, input_channnel, classes)
            rgb_model_2 =  Net(mid_channel, input_channnel, classes)
            rgb_model_1=torch.nn.DataParallel(rgb_model_1)
            rgb_model_2=torch.nn.DataParallel(rgb_model_2)
            rgb_model = [rgb_model_1, rgb_model_2]

        if args.model=="MSTCN":
            print("you are processing MSTCN")
            from models  import MultiStageModel as Net
            rgb_model = Net(num_stages=1, num_layers=5, num_f_maps=512, dim=1024, num_classes=51)


        

        if args.load_model!= "False":
            rgb_model.load_state_dict(torch.load(str(args.load_model)))
            print("loaded",args.load_model)

        pytorch_total_params = sum(p.numel() for p in rgb_model[0].parameters() if p.requires_grad)
        print('pytorch_total_params', pytorch_total_params)
        print('num_channel:', num_channel, 'input_channnel:', input_channnel,'num_classes:', num_classes)
        rgb_model_1.cuda()
        rgb_model_2.cuda()

        criterion = nn.NLLLoss(reduce=False)
        lr = float(args.lr)
        params = list(rgb_model_1.parameters())+list(rgb_model_2.parameters())
        optimizer = optim.Adam(params, lr=lr)
        lr_sched = optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=8, verbose=True)
        run([(rgb_model, 0, dataloaders, optimizer, lr_sched, args.comp_info)], criterion, num_epochs=int(args.epoch))



