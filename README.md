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

* [Balanced and Unbalanced Datset](#datasets)




## Folders overview.

<a href="https://www.google.com/" target="_blank">Google</a>

## Steps to Training.


## Dependencies.

## References.

[1]. Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset, CVPR 2017

<a href="https://arxiv.org/abs/2010.14982" target="_blank">[2]. Toyota Smarthome Untrimmed: Real-World Untrimmed Videos for Activity Detection.</a>



