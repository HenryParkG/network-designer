# 레이어 템플릿 정의
LAYER_TEMPLATES = {
    "Linear": {"class":"nn.Linear","params":{"in_features":128,"out_features":64,"bias":True},"friendly":"Linear(in,out)"},
    "Conv2d": {"class":"nn.Conv2d","params":{"in_channels":3,"out_channels":16,"kernel_size":3,"stride":1,"padding":0,"bias":True},"friendly":"Conv2d(Cin,Cout,k)"},
    "ReLU": {"class":"nn.ReLU","params":{"inplace":False},"friendly":"ReLU()"},
    "Flatten": {"class":"nn.Flatten","params":{"start_dim":1,"end_dim":-1},"friendly":"Flatten()"},
    "Dropout": {"class":"nn.Dropout","params":{"p":0.5,"inplace":False},"friendly":"Dropout(p)"},
    "BatchNorm2d": {"class":"nn.BatchNorm2d","params":{"num_features":16},"friendly":"BatchNorm2d(num_features)"},
    "MaxPool2d": {"class":"nn.MaxPool2d","params":{"kernel_size":2,"stride":2},"friendly":"MaxPool2d(k)"},
    "AvgPool2d": {"class":"nn.AvgPool2d","params":{"kernel_size":2,"stride":2},"friendly":"AvgPool2d(k)"},
    "LSTM": {"class":"nn.LSTM","params":{"input_size":128,"hidden_size":64,"num_layers":1,"batch_first":True},"friendly":"LSTM(in,hidden)"}
}
