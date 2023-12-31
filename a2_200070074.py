# -*- coding: utf-8 -*-
"""A2_200070074.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DDJHUWZfywJyJCth2zsFx5leqCFiNATE

Importing Libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn as sk

"""Importing training and testing data"""

train_data=pd.read_csv("https://www.ee.iitb.ac.in/~asethi/Dump/MouseTrain.csv")                         #importing the data
test_data=pd.read_csv("https://www.ee.iitb.ac.in/~asethi/Dump/MouseTest.csv")

"""Exploratory data analysis :

1.   we will remove columns with number of null values more than 70 as there are total 760 values in each coloumn
2.Remove columns those are highly correlated with each other
"""

waste_columns=set()                                                     # Created a set to collect the columns which are not useful
for i in train_data.columns :
  no_of_zeroes=train_data[i].isna().sum()
  if no_of_zeroes>=70 :                                                 #calculating the number of NaN in a column
    waste_columns.add(i)                                                # Including all the columns which are not usefull
print(waste_columns)

######################################################################

corelation_matrix=train_data.corr()
corelation_matrix=corelation_matrix.abs()                               # Absolute corelation matrix
corelation_matrix
upper_traingle=np.triu(corelation_matrix,1)
print(upper_traingle)                                                   # taking only upper traingle for the corelation matrix as it is symmetric 
for i in range(upper_traingle.shape[0]) :
  for j in upper_traingle[:,i]:
    if j>=0.95 :                                                        #Threshold is 0.95
      waste_columns.add(corelation_matrix.columns[i])
print(waste_columns)                                                    #printing all the columns which are not useful bcz of more number of NaN vales and high correlation between columns

########################################################################

"""We have to delete coulmns that are not usefull to any more"""

train_data_new=train_data                                                   # created two new data sets which contains only useful data
test_data_new=test_data
for i in waste_columns:
  train_data_new=train_data_new.drop([i],axis=1)                            # dropping a column in each iteration
  test_data_new=test_data_new.drop([i],axis=1)

"""As there are some missing values in the data, To impute them I am using IterativeImputer."""

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer                                                                         #multi varaible imputation function, we are using this for imputation
train_data_proteins=train_data_new.drop(['Genotype','Treatment_Behavior'],axis=1)                                   # removing columns which conntains target values 
imp = IterativeImputer(max_iter=10, random_state=0)
imp.fit(train_data_proteins)
train_data_proteins_imputed=imp.transform(train_data_proteins)                                                      # numpy array containing all the protein values imputed

#checking
print(np.sum(np.isnan(train_data_proteins_imputed)))                                                                #prints the number of NaN in a array

#####################################################################

test_data_proteins=test_data_new.drop(['Genotype','Treatment_Behavior'],axis=1)
imp = IterativeImputer(max_iter=10, random_state=0)
imp.fit(test_data_proteins)                                                                                          #same as above but this for tesing part
test_data_proteins_imputed=imp.transform(test_data_proteins)
#testing

#checking
print(np.sum(np.isnan(test_data_proteins_imputed)))

"""To check whether classes are balanced or not"""

class_genotype=train_data_new.groupby(['Genotype']).size()                                 # It will split the data into different groups and gives the size of each group
class_TrtmtBehav=train_data_new.groupby(['Treatment_Behavior']).size()
print(class_genotype)
print(class_TrtmtBehav)

"""Here we can observe that Classes for Genotype Classification are almost balanced, whereas for Treatment Behaviour Classification are not that balanced

Extracting the target values from the  data sets for future purposes
"""

genotype_train=train_data_new['Genotype'].to_numpy()                                               #extracting the Genotype  column from the train dataset as a numpy array
genotype_test=test_data_new['Genotype'].to_numpy()                                                 #extracting the Genotype  column from  the test dataset as a numpy array
TrtmtBehav_train=train_data_new['Treatment_Behavior'].to_numpy()                                   #extracting the Treatment behavior column from the train dataset as a numpy array
TrtmtBehav_test=test_data_new['Treatment_Behavior'].to_numpy()                                     #extracting the Treatment behavior  column from the test dataset as a numpy array

"""Importing useful libraries for the coming questions"""

from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import classification_report

"""Linear SVM with regularization as hyperparameter"""

linear_svc_geno =SVC(kernel='linear')                                                            # creating a object for linear svm model using SVM from sklearn library
param_grid = {'C': [0.01,0.1, 1, 10,100,1000]}                                                   # continous values of hyperparameter C for linear SVM
linear_svc_geno_GridsearchCV = GridSearchCV(linear_svc_geno, param_grid)                         # creating a Gridsearch model for linear SVM and the hyper parameter C
linear_svc_geno_GridsearchCV.fit(train_data_proteins_imputed, genotype_train)                    # fitting the above model for train_data and there target values to get the best model fom it
linear_svc_geno= linear_svc_geno_GridsearchCV.best_estimator_                                    # Taking the best model after doing the GridSearchCV 
linear_svc_geno_para = linear_svc_geno_GridsearchCV.best_params_                                 # Values of hyperparameters that are giving the best model
linear_svc_geno_results=pd.DataFrame(linear_svc_geno_GridsearchCV.cv_results_)                   # Score of various cross validation results 
print(linear_svc_geno_para)
linear_svc_geno_results[linear_svc_geno_results.columns[5:]]                                     # One with low rank is the best model

"""Its is almost similiar to the above one but instead of using Genometype as target varaible, we are using Treatment_Behavior which is a Quaternary Classification"""

linear_svc_TrtmtBehav =SVC(kernel='linear')                                 
param_grid = {'C': [0.1,1,10,100,1000,10000]}
linear_svc_TrtmtBehav_GridsearchCV = GridSearchCV(linear_svc_TrtmtBehav, param_grid)                      
linear_svc_TrtmtBehav_GridsearchCV.fit(train_data_proteins_imputed, TrtmtBehav_train)
linear_svc_TrtmtBehav= linear_svc_TrtmtBehav_GridsearchCV.best_estimator_                                      
linear_svc_TrtmtBehav_para = linear_svc_TrtmtBehav_GridsearchCV.best_params_
linear_svc_TrtmtBehav_results=pd.DataFrame(linear_svc_TrtmtBehav_GridsearchCV.cv_results_)
print(linear_svc_TrtmtBehav_para)
linear_svc_TrtmtBehav_results[linear_svc_TrtmtBehav_results.columns[5:]]

"""RBF kernel SVM with kernel width and regularization as hyperparameters"""

rbf_svc_geno =SVC()                                                                              # creating a object for rbf kernel svm model using SVM from sklearn librar
param_grid = {'C': [ 1, 10,100,1000,10000],'gamma': [0.00001,0.0001,0.001,0.01,0.1,1]}           # continous range  values of hyperparameters C and gamma for rbf kernel svm 
rbf_svc_geno_GridsearchCV = GridSearchCV(rbf_svc_geno, param_grid)                               # creating a Gridsearch model for rbf kernel SVM and the hyper parameter C, gamma
rbf_svc_geno_GridsearchCV.fit(train_data_proteins_imputed, genotype_train)                       # fitting the above model for train_data and there target values to get the best model fom it
rbf_svc_geno= rbf_svc_geno_GridsearchCV.best_estimator_                                          # Taking the best model after doing the GridSearchCV 
rbf_svc_geno_para = rbf_svc_geno_GridsearchCV.best_params_                                       # Values of hyperparameters that are giving the best model
rbf_svc_geno_results=pd.DataFrame(rbf_svc_geno_GridsearchCV.cv_results_)                         # Score of various cross validation results
print(rbf_svc_geno_para)
rbf_svc_geno_results[rbf_svc_geno_results.columns[6:]]                                           # One with low rank is the best model

"""Its is almost similiar to the above one but instead of using Genometype as target varaible, we are using Treatment_Behavior which is a Quaternary Classification"""

rbf_svc_TrtmtBehav =SVC()
param_grid = {'C': [ 1, 10,100,1000,10000],'gamma': [0.00001,0.0001,0.001,0.01,0.1,1]}
rbf_svc_TrtmtBehav_GridsearchCV = GridSearchCV(rbf_svc_TrtmtBehav, param_grid)                      
rbf_svc_TrtmtBehav_GridsearchCV.fit(train_data_proteins_imputed, TrtmtBehav_train)
rbf_svc_TrtmtBehav= rbf_svc_TrtmtBehav_GridsearchCV.best_estimator_
rbf_svc_TrtmtBehav_para = rbf_svc_TrtmtBehav_GridsearchCV.best_params_
rbf_svc_TrtmtBehav_results=pd.DataFrame(rbf_svc_TrtmtBehav_GridsearchCV.cv_results_)
print(rbf_svc_TrtmtBehav_para)
rbf_svc_TrtmtBehav_results[rbf_svc_TrtmtBehav_results.columns[6:]]

"""Neural network with single ReLU hidden layer and Softmax output (hyperparameters: number of
neurons, weight decay)
"""

neural_network_geno = MLPClassifier(max_iter=2000)                                                      # creating a object for neural network model using MLPClassifier from sklearn library
param_grid = {'hidden_layer_sizes': [8,16,32,64,128],'alpha': [0.00001,0.0001, 0.001, 0.01, 0.1]}       # continous range  values of hyperparameters hidden layer sizes  and alpha for neural network
neural_network_geno_GridsearchCV = GridSearchCV(neural_network_geno, param_grid)                        # creating a Gridsearch model for the neural network and the hyper parameters hidden layer sizes, alpha
neural_network_geno_GridsearchCV.fit(train_data_proteins_imputed, genotype_train)                       # fitting the above model for train_data and there target values to get the best model fom it
neural_network_geno= neural_network_geno_GridsearchCV.best_estimator_                                   # Taking the best model after doing the GridSearchCV 
neural_network_geno_para = neural_network_geno_GridsearchCV.best_params_                                # Values of hyperparameters that are giving the best model
neural_network_geno_results=pd.DataFrame(neural_network_geno_GridsearchCV.cv_results_)                  # Score of various cross validation rltesus
print(neural_network_geno_para)
neural_network_geno_results[neural_network_geno_results.columns[6:]]                                    # One with low rank is the best model

"""Its is almost similiar to the above one but instead of using Genometype as target varaible, we are using Treatment_Behavior which is a Quaternary Classification"""

neural_network_TrtmtBehav = MLPClassifier(max_iter=2000)
param_grid = {'hidden_layer_sizes': [8,16,32,64,128],'alpha': [0.00001,0.0001, 0.001, 0.01, 0.1]}
neural_network_TrtmtBehav_GridsearchCV = GridSearchCV(neural_network_TrtmtBehav, param_grid)                      
neural_network_TrtmtBehav_GridsearchCV.fit(train_data_proteins_imputed, TrtmtBehav_train)
neural_network_TrtmtBehav= neural_network_TrtmtBehav_GridsearchCV.best_estimator_
neural_network_TrtmtBehav_para = neural_network_TrtmtBehav_GridsearchCV.best_params_
neural_network_TrtmtBehav_results=pd.DataFrame(neural_network_TrtmtBehav_GridsearchCV.cv_results_)
print(neural_network_TrtmtBehav_para)
neural_network_TrtmtBehav_results[neural_network_TrtmtBehav_results.columns[6:]]

"""Random forest (max tree depth, max number of variables per node)"""

random_forest_geno= RandomForestClassifier(random_state=42)                                               # creating a object for random forest model using RandomforestClassifier from sklearn librar
param_grid = {'max_features': ['sqrt','log2',None,0.8],'max_depth': [8,10,14,18,22]}                      # continous range  values of hyperparameters max depth  and max_features for Random forest
random_forest_geno_GridsearchCV = GridSearchCV(random_forest_geno, param_grid)                            # creating a Gridsearch model for the neural network and the hyper parameters 
random_forest_geno_GridsearchCV.fit(train_data_proteins_imputed, genotype_train)                          # fitting the above model for train_data and there target values to get the best model fom it
random_forest_geno= random_forest_geno_GridsearchCV.best_estimator_                                       # Taking the best model after doing the GridSearchCV
random_forest_geno_para = random_forest_geno_GridsearchCV.best_params_                                    # Values of hyperparameters that are giving the best model
random_forest_geno_results=pd.DataFrame(random_forest_geno_GridsearchCV.cv_results_)                      # Score of various cross validation rltesus
print(random_forest_geno_para)
random_forest_geno_results[random_forest_geno_results.columns[6:]]                                        # One with low rank is the best model

"""Its is almost similiar to the above one but instead of using Genometype as target varaible, we are using Treatment_Behavior which is a Quaternary Classification"""

random_forest_TrtmtBehav= RandomForestClassifier(random_state=42)
param_grid = {'max_features': ['sqrt','log2',None,0.8],'max_depth': [10,14,18,22,26]}
random_forest_TrtmtBehav_GridsearchCV = GridSearchCV(random_forest_TrtmtBehav, param_grid)                      
random_forest_TrtmtBehav_GridsearchCV.fit(train_data_proteins_imputed, TrtmtBehav_train)
random_forest_TrtmtBehav= random_forest_TrtmtBehav_GridsearchCV.best_estimator_
random_forest_TrtmtBehav_para = random_forest_TrtmtBehav_GridsearchCV.best_params_
random_forest_TrtmtBehav_results=pd.DataFrame(random_forest_TrtmtBehav_GridsearchCV.cv_results_)
print(random_forest_TrtmtBehav_para)
random_forest_TrtmtBehav_results[random_forest_TrtmtBehav_results.columns[6:]]

"""Feature importance for each model to see if the same proteins are important for each model"""

linear_feature_importance = abs(linear_svc_geno.coef_[0])                         # we using .coef_ to get the feature impotance of every protein
linear_feature_importance = pd.DataFrame(data=linear_feature_importance, index = train_data_new.columns[:-2])        # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(linear_feature_importance.index, linear_feature_importance[0])                      #plotting script
plt.xticks(rotation=90)
plt.title("Linear SVM for Genotype")
plt.show()

nn_feature_importance = abs(np.mean(neural_network_geno.coefs_[0], axis=1))                 # we using .coef_ to get the feature impotance of every protein and we are taking the mean of all the weights are there will many layers
nn_feature_importance = pd.DataFrame(data=nn_feature_importance, index = train_data_new.columns[:-2])           # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(nn_feature_importance.index, nn_feature_importance[0])
plt.xticks(rotation=90)
plt.title("Neural Networks for Genotype")
plt.show()

rf_feature_importance = random_forest_geno.feature_importances_                  # for random forest we can directly use the feature_impotance  function to get the values
rf_feature_importance = pd.DataFrame(data=rf_feature_importance, index =  train_data_new.columns[:-2])        # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(rf_feature_importance.index, rf_feature_importance[0])
plt.xticks(rotation=90)
plt.title("Random Forest for Genotype")
plt.show()

"""By observing every plot we can see that there are some proteins which have more feature importance in every model 

1.   APP_N                 
2.   GluR3
3.   pNR1_N
4.   Tau_N
5.   NR2B_N
6.   MTOR_N

Following plots are for the Quaternary Classification
"""

linear_feature_importance = abs(linear_svc_TrtmtBehav.coef_[0])                                         # we using .coef_ to get the feature impotance of every protein
linear_feature_importance = pd.DataFrame(data=linear_feature_importance, index = train_data_new.columns[:-2])        # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(linear_feature_importance.index, linear_feature_importance[0])                                          #plotting script
plt.xticks(rotation=90)
plt.title("Linear SVM for Genotype")
plt.show()

nn_feature_importance = abs(np.mean(neural_network_TrtmtBehav.coefs_[0], axis=1))                                   # we using .coef_ to get the feature impotance of every protein
nn_feature_importance = pd.DataFrame(data=nn_feature_importance, index =  train_data_new.columns[:-2])              # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(nn_feature_importance.index, nn_feature_importance[0])                                                     #plotting script
plt.xticks(rotation=90)
plt.title("Neural Networks for Genotype")
plt.show()

rf_feature_importance = random_forest_TrtmtBehav.feature_importances_                                 # for random forest we can directly use the feature_impotance  function to get the values
rf_feature_importance = pd.DataFrame(data=rf_feature_importance, index =  train_data_new.columns[:-2]) # converting the array into a data frame
plt.figure(figsize=(25,5))
plt.bar(rf_feature_importance.index, rf_feature_importance[0])                                          #plotting script
plt.xticks(rotation=90)
plt.title("Random Forest for Genotype")
plt.show()

"""By observing every plot we can see that there are some proteins which have more feature importance in every model 

1.   SOD1_N              
2.   pERK_N
3.   DYRK1A_N
4.   pPKCAB_N
5.   pP7056_N
6.   CaNA_N

Removing some features systematically using RFECV.
It is done only for Linear svm and random forest.
"""

from sklearn.feature_selection import RFECV
linear_selector = RFECV(linear_svc_geno)
linear_selector = linear_selector.fit(train_data_proteins_imputed, genotype_train)
linear_mask = linear_selector.support_                          # array containing True and False , if it is True then it is useful else not useful
print(linear_mask)

linear_selector = RFECV(linear_svc_TrtmtBehav)
linear_selector = linear_selector.fit(train_data_proteins_imputed, TrtmtBehav_train)
linear_mask = linear_selector.support_                                        # array containing True and False , if it is True then it is useful else not useful
print(linear_mask)

random_forest_selector = RFECV(random_forest_geno)
random_forest_selector = linear_selector.fit(train_data_proteins_imputed, genotype_train)
random_forest_mask = random_forest_selector.support_                                  # array containing True and False , if it is True then it is useful else not useful
print(random_forest_mask)

random_forest_selector = RFECV(random_forest_TrtmtBehav)
random_forest_selector = linear_selector.fit(train_data_proteins_imputed, TrtmtBehav_train)
random_forest_mask = random_forest_selector.support_                        # array containing True and False , if it is True then it is useful else not useful
print(random_forest_mask)

"""Testing the models on test data"""

linear_test_pred = linear_svc_geno.predict(test_data_proteins_imputed)
linear_test_report = classification_report(genotype_test, linear_test_pred)
print(linear_test_report)

"""precison for TS65DN is not good at all,f1_score is not very much high in this linear svm"""

rbf_test_pred = rbf_svc_geno.predict(test_data_proteins_imputed)
rbf_test_report = classification_report(genotype_test, rbf_test_pred)
print(rbf_test_report)

"""f1_score is increased overall but for Ts65Dn it is unchanged and precision is also increased"""

nn_test_pred = neural_network_geno.predict(test_data_proteins_imputed)
nn_test_report = classification_report(genotype_test, nn_test_pred)
print(nn_test_report)

"""Precison and F1_score bith are very poor when compared with the above models"""

random_forest_test_pred = random_forest_geno.predict(test_data_proteins_imputed)
random_forest_test_report = classification_report(genotype_test, random_forest_test_pred)
print(random_forest_test_report)

"""F1_score is best in random forest when compared with other models"""

linear_test_pred = linear_svc_TrtmtBehav.predict(test_data_proteins_imputed)
linear_test_report = classification_report(TrtmtBehav_test, linear_test_pred)
print(linear_test_report)

"""F1 score for linear svm is ok neither very high nor low"""

rbf_test_pred = rbf_svc_TrtmtBehav.predict(test_data_proteins_imputed)
rbf_test_report = classification_report(TrtmtBehav_test, rbf_test_pred)
print(rbf_test_report)

"""F1_score decreased more rapidly and it is very poor here"""

nn_test_pred = neural_network_TrtmtBehav.predict(test_data_proteins_imputed)
nn_test_report = classification_report(TrtmtBehav_test, nn_test_pred)
print(nn_test_report)

"""It has F1_score even lesser than rbf kernel svm and very poor"""

random_forest_test_pred = random_forest_TrtmtBehav.predict(test_data_proteins_imputed)
random_forest_test_report = classification_report(TrtmtBehav_test, random_forest_test_pred)
print(random_forest_test_report)

"""Random forest has also very poor f1_score

Overall

1.  for binary classification ,i.e, for Genotype RandomForest classification is the best model with weighted F1_score=0.82

2.  for Quaternary Classification,i.e, for treatment behavior  Linear SVM is the best mode with weighted F1_score= 0.85

Objective 2
"""

from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import torch.backends.cudnn as cudnn                                           #importing required libraries
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy

cudnn.benchmark = True
plt.ion()   # interactive mode

"""L0ading the data"""

! curl 'https://download.pytorch.org/tutorial/hymenoptera_data.zip' -O
! unzip -q hymenoptera_data.zip
! mkdir data
! mv hymenoptera_data data
! mv sample_data data

"""Data augmentation and normalization for training"""

# Data augmentation and normalization for training
# Just normalization for validation
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

data_dir = 'data/hymenoptera_data'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
                                          data_transforms[x])
                  for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
                                             shuffle=True, num_workers=4)
              for x in ['train', 'val']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

"""Visualize a few images"""

def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)  # pause a bit so that plots are updated


# Get a batch of training data
inputs, classes = next(iter(dataloaders['train']))

# Make a grid from batch
out = torchvision.utils.make_grid(inputs)

imshow(out, title=[class_names[x] for x in classes])

"""Training a model"""

def train_model(model, criterion, optimizer, scheduler, num_epochs=25):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val Acc: {best_acc:4f}')

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model

"""Loading pretrained ResNet model for feature extraction"""

model_conv = torchvision.models.resnet18(pretrained=True)
for param in model_conv.parameters():
    param.requires_grad = False

# Parameters of newly constructed modules have requires_grad=True by default
num_ftrs = model_conv.fc.in_features
model_conv.fc = nn.Linear(num_ftrs, 2)

model_conv = model_conv.to(device)

criterion = nn.CrossEntropyLoss()

# Observe that only parameters of final layer are being optimized as
# opposed to before.
optimizer_conv = optim.SGD(model_conv.fc.parameters(), lr=0.001, momentum=0.9)

# Decay LR by a factor of 0.1 every 7 epochs
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_conv, step_size=7, gamma=0.1)

model_ft = train_model(model_conv, criterion, optimizer_conv, exp_lr_scheduler,
                       num_epochs=5)

"""Visualizing the model predictions"""

def visualize_model(model, num_images=6):
    was_training = model.training
    model.eval()
    images_so_far = 0
    fig = plt.figure()

    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloaders['val']):
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            for j in range(inputs.size()[0]):
                images_so_far += 1
                ax = plt.subplot(num_images//2, 2, images_so_far)
                ax.axis('off')
                ax.set_title(f'predicted: {class_names[preds[j]]}')
                imshow(inputs.cpu().data[j])

                if images_so_far == num_images:
                    model.train(mode=was_training)
                    return
        model.train(mode=was_training)

visualize_model(model_conv)
plt.ioff()
plt.show()

"""Summary : 

1.  for given data in objective 1, for binary classfication RandomForest is the best model
2.   for quatanary classifcation, Linear SVM is the best model 
3.In objective2 , I have just check whether given code is running or not




"""