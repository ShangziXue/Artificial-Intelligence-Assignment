import argparse
import csv
import time

import numpy as np
from sklearn import preprocessing

import KNN
import SVM
import LR


def loadData(file, Normalize=False, Methods='NearestNeighbors'):
    '''
    加载数据集
    ========
    Arguments
    ---------
    - `file` 数据集文件
    - `Normalize` 是否进行标准化
    - `Methods` 为不同学习方法做处理
        - `'NearestNeighbors'` k-近邻算法，类别标签为 0-不及格与 1-及格
        - `'LogisticRegression'` Logistic 回归算法，类别标签为 0-不及格与 1-及格
        - `'SupportVectorMachine'` 支持向量机算法，类别标签为 -1-不及格与 1-及格

    Returns
    -------
    - `Data_withG1G2` 包含属性G1 G2的数据集
    - `Data_withoutG1G2` 不包含属性G1 G2的数据集
    - `Label` 指示是否及格的标签集
    '''
    print('start reading ' + file)
    Attributes = [[] for i in range(30)]  # 转置的属性列表
    Grades = []
    Label = []
    labelEncoder = preprocessing.LabelEncoder()
    with open(file, 'r') as fileStream:
        lines = csv.reader(fileStream, delimiter=';')
        next(lines)  # 跳过表头
        for line in lines:
            for i in [0, 1, 3, 4, 5, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22]:  # binary or nominal
                Attributes[i].append(line[i])
            for i in [2, 6, 7, 12, 13, 14, 23, 24, 25, 26, 27, 28, 29]:  # numeric
                Attributes[i].append(int(line[i]))
            Grades.append([int(num) for num in line[30:32]])  # 31:G1 32:G2
            # G3 >= 10 为及格
            Label.append(
                1 if int(line[-1]) >= 10 else (-1 if Methods == 'SupportVectorMachine' else 0))
        for i in [0, 1, 3, 4, 5, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22]:
            Attributes[i] = labelEncoder.fit_transform(Attributes[i])  # 编码为整数
        Data_withoutG = np.array(Attributes).T  # 转置属性

        if Normalize == True:
            upperBounds = [1, 1, 22, 1, 1, 1, 4, 4, 4, 4, 3, 2, 4,
                           4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 93]  # 属性上界
            lowerBounds = [0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                           1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0]  # 属性下界

            Data_withoutG = Data_withoutG.astype(np.float64)  # 转换为浮点类型

            for i in range(Data_withoutG.shape[0]):
                for j in range(30):
                    Data_withoutG[i, j] = (
                        Data_withoutG[i, j] - lowerBounds[j]) / (upperBounds[j] - lowerBounds[j])
            Grades = np.array(Grades, dtype=float) / 20

    return list(np.hstack((Data_withoutG, Grades))), Data_withoutG, Label


def modelTest(testLabel, predictLabel):
    '''
    测试模型正确率
    ===========
    Arguments
    ---------
    - `testLabel` 测试集标签
    - `predictLabel` 预测模型预测标签

    Returns
    -------
    - 模型正确率
    '''

    truePositive = falsePositive = falseNegative = trueNegative = 0
    for i in range(len(testLabel)):
        if predictLabel[i] == 1:
            if testLabel[i] == 1:
                truePositive += 1
            else:
                falsePositive += 1
        else:
            if testLabel[i] == 1:
                falseNegative += 1
            else:
                trueNegative += 1

    print('TP = {:3}  TN = {:3}'.format(truePositive, trueNegative))
    print('FP = {:3}  FN = {:3}'.format(falsePositive, falseNegative))

    if truePositive == 0:
        return 0

    precision = truePositive / (truePositive + falsePositive)
    recall = truePositive / (truePositive + falseNegative)

    return (2 * precision * recall) / (precision + recall)


def gridSearch_Gaussian(trainData, trainLabel, testData, testLabel):
    '''
    网格搜索高斯核参数
    ==============
    '''
    C = [np.power(2.0, i) for i in range(-5, 16, 2)]
    Sigma = [np.power(2.0, i) for i in range(-3, 8)]
    Epsilon = [np.power(10.0, i) for i in range(-6, 0)]
    subRange = 100

    maximumArguments = (0, 0, 0)
    maximumF1Score = 0
    for c, sigma, epsilon in [(c, sigma, epsilon) for c in C for sigma in Sigma for epsilon in Epsilon]:
        print(c, sigma, epsilon)
        predictLabel = SVM.predict(
            trainData[:subRange], trainLabel[:subRange], testData, C=c, sigma=sigma, epsilon=epsilon)
        f1Score = modelTest(testLabel, predictLabel)
        if f1Score > maximumF1Score:
            maximumF1Score = f1Score
            maximumArguments = (c, sigma, epsilon)
    print(maximumF1Score, maximumArguments)


if __name__ == "__main__":
    # 命令行参数分析
    parser = argparse.ArgumentParser(
        description='Simple machine learning test', epilog='PB17000297 罗晏宸 AI Programming Assignment 2', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(
        title='Learning Algorithms', dest='algorithm', required=True)

    parser_KNN = subparsers.add_parser(
        'KNN', help='k-Nearest Neighbors', description='k-Nearest Neighbors', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_KNN.add_argument('-K', default=27, type=int,
                            help='Number of chosen neighbors')

    parser_SVM = subparsers.add_parser(
        'SVM', help='Support Vector Machine', description='Support Vector Machine', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_SVM.add_argument('-C', metavar='penalty', default=200, type=int,
                            help='Soft margin penalty hyperparameter for support vector machine')
    parser_SVM.add_argument('-t', '--toler', metavar='xi', dest='epsilon', default=0.0001,
                            type=float, help='Slack variable (toler) for support vector machine')

    subsubparsers = parser_SVM.add_subparsers(
        title='Kernel Functions', dest='kernel')

    parser_Gaussian = subsubparsers.add_parser(
        'Gaussian', help='Gaussian kernel function(default)', description='Gaussian kernel function', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_Gaussian.add_argument('-s', '--sigma', metavar='sigma', default=10, type=int,
                                 help='Parameter of gaussian kernel function for support vector machine')

    parser_Linear = subsubparsers.add_parser(
        'Linear', help='Linear kernel function', description='Linear kernel function', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser_Polynomial = subsubparsers.add_parser(
        'Polynomial', help='Polynomial kernel function', description='Polynomial kernel function', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_Polynomial.add_argument('-p', default=2, type=int,
                                   help='Parameter of polynomial kernel function for support vector machine')

    parser_LR = subparsers.add_parser(
        'LR', help='Logistic Regression', description='Logistic Regression', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_LR.add_argument('-i', '--iteration', metavar='i', dest='iteration',
                           default=200, type=int, help='Number of iteration')
    parser_LR.add_argument('-r', '--rate', metavar='alpha', dest='learning_rate',
                           default=0.0001, type=float, help='Rate of learning')

    args = parser.parse_args()

    if args.algorithm == 'SVM' and args.kernel == None:  # 默认核函数
        args.kernel = 'Gaussian'
        args.sigma = 10

    start = time.time()

    if args.algorithm == 'KNN':  # k-近邻算法
        trainData, _, trainLabel = loadData(
            '../data/student/student-por.csv', Methods='NearestNeighbors')  # 训练数据

        testData, _, testLabel = loadData(
            '../data/student/student-mat.csv', Methods='NearestNeighbors')  # 测试数据

        predictLabel = KNN.predict(trainData, trainLabel, testData, K=args.K)

    elif args.algorithm == 'SVM':  # 支持向量机算法
        trainData, _, trainLabel = loadData(
            '../data/student/student-por.csv', Normalize=True, Methods='SupportVectorMachine')  # 训练数据

        testData, _, testLabel = loadData(
            '../data/student/student-mat.csv', Normalize=True, Methods='SupportVectorMachine')  # 测试数据

        predictLabel = SVM.predict(trainData, trainLabel, testData, C=args.C, epsilon=args.epsilon, kernel=args.kernel,
                                   sigma=args.sigma if args.kernel == 'Gaussian' else None, p=args.p if args.kernel == 'Polynomial' else None)

    elif args.algorithm == 'LR':  # Logistic 回归算法
        trainData, _, trainLabel = loadData(
            '../data/student/student-por.csv', Methods='LogisticRegression')  # 训练数据

        testData, _, testLabel = loadData(
            '../data/student/student-mat.csv', Methods='LogisticRegression')  # 测试数据

        predictLabel = LR.predict(trainData, trainLabel, testData,
                                  iteration=args.iteration, learning_rate=args.learning_rate)

    # gridSearch_Gaussian(trainData, trainLabel, testData, testLabel)

    end = time.time()
    print('Elapsed time: {:.4}s'.format(end - start))
    print('F1 score: {:%}'.format(modelTest(testLabel, predictLabel)))
