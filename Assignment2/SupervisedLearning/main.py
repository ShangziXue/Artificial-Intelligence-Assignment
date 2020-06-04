import numpy as np
import time
import csv
from sklearn import preprocessing


def loadData(file):
    '''
    ## 加载数据集
    ### Arguments
    - `file` 数据集文件

    ### Returns
    - `Data_withG1G2` 包含属性G1 G2的数据集
    - `Data_withoutG1G2` 不包含属性G1 G2的数据集
    - `Label` 指示是否及格的标签集
    '''
    print('start reading file')
    Attributes = [[] for i in range(30)]  # 转置的属性列表
    Grades = []
    Label = []
    labelEncoder = preprocessing.LabelEncoder()
    with open(file, 'r') as fileStream:
        lines = csv.reader(fileStream, delimiter=';')
        next(lines)  # 跳过表头
        for line in lines:
            for i in [0, 1, 3, 4, 5, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22]:
                Attributes[i].append(line[i])
            for i in [2, 6, 7, 12, 13, 14, 23, 24, 25, 26, 27, 28, 29]:
                Attributes[i].append(int(line[i]))
            Grades.append([int(num) for num in line[30:32]])  # 31:G1 32:G2
            Label.append(1 if int(line[-1]) >= 10 else 0)  # G3 >= 10 为及格
        for i in [0, 1, 3, 4, 5, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22]:
            Attributes[i] = labelEncoder.fit_transform(Attributes[i])  # 编码为整数
        Data_withoutG = np.array(Attributes).T  # 转置属性
    return list(np.hstack((Data_withoutG, Grades))), Data_withoutG, Label


if __name__ == "__main__":
    start = time.time()

    # 获取训练集
    trainData, _, trainLabel = loadData('../DataSet/student/student-mat.csv')

    print(trainData[2])
    print(trainLabel[2])

    end = time.time()

    print('time span:', end - start)
