# Joint view action detection in indoor scenarios
The goal of the project is combine footage of same scenario taken by two different cameras placed in 2 diffrerent places and then perform action recognition. This repositry includes various experiments that were perormed inconjunction with joint view.

<img src="/gifs/Sit_down_v1.gif" width="300" height="200"/> <img src="/gifs/Sit_down_v2.gif" width="300" height="200"/> 



## Introduction.

Joint view action detection/recognition is nothing but combining footage of same scenarios captured in different views to perform action detetction. This is a challenging task for any current state of the art action recognition methods because there is a huge difference in visual features across different views even though the scenario is same. The main aim of the project is to obtain a combined feature level representation/embedding from different views that can be used to improve action detection perdformance.This is done in two steps.

1). First we extract the spatio-embeddings of the videos using a pre-trained 3D-CNN network in our case its I3D[1].

2). Then a 2 stream TCN network is used to perform action detection wherein each stream is inputted with a embedding from a particular view and similarily with the other stream.

The main dataset that we used in this project is Toyota smarthome untrimmed dataset[2].

## Experiments and Terminology.
Along with joint view we have performed various experiments on the Toyota untrimmed smarthome dataset and have named each folder accordingly. The essential terms necessary to understand the project are .

#### 1). Balanced and Unbalanced Datset.

The original Toyota untrimmed smarthome video dataset has close to 51 actions and the frequency of the occurence of this actions in the videos is highly unbalanced meaning certain actions occur more frequently than other actions and hence this is the reason we call it unbalanced datset. Later on in one of the [experiment](https://github.com/hari431996/joint_view_action_detection/tree/main/balanced_data_un_synchronised_footage%20) we removed certain low frequency actions and obtained a final balanced dataset consiting of only 34 highly occuring actions.

#### 2). Synchronised and unsynchronised.
Given a pair of videos of  two different views  of same scenario, should have overlapping footage or in other words they should have starting and end points in which the scenario is same but from different views, this is what we mean by synchronised footage. In the original Toyota untrimmed smarthome dataset there are close to 536 videos and a given pair of videos have non overlapping starting points but whereas in a synchronised pair there are only 298 videos and given pair of videos have starting and ending points with overlapping footage. Hence, the major difference between synchronised and unsynchronised is that the last one has more runtime than compared to synchronised videos.

#### 3). Joint View.
In joint view we utilise features from video pairs of two different views. There are close to 298 videos thereby giving us a pair of 149 videos. The features from this pairs of videos with different views are combined at various stages of a 2-Stream TCN network like for example late [fusion](https://github.com/hari431996/joint_view_action_detection/tree/main/joint_view_late_fusion).



## Folders overview.
There are 5 main folders, each refering to a particular experiment that was performed. Each folder consists of few important files necesary to run the experiment, of these the most important files are.

1). models_xxx - This file basically contains network architecture/backbone.

2). smarthome_i3d_per_xxx - This file contains the dataloader necessary to fit the model.

3). train_xx - This file contains the code to train the model.

4). run_xx.sh - This file is a shell script that is necessary to run the model. Note - Please read carefully about each argument before running the experiment.

Also note that each folder has a file ending with .json extension which is the dataset that has to be used and the file has been named in accordance with the experiment as explained below.
##### 1). balanced_data_un_synchronised_footage experiment.

This is a simple experiment with 





## Steps to Training.


## Dependencies.

## References.

[1]. Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset, CVPR 2017

<a href="https://arxiv.org/abs/2010.14982" target="_blank">[2]. Toyota Smarthome Untrimmed: Real-World Untrimmed Videos for Activity Detection.</a>



