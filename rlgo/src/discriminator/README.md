# LLM-Based Code Clustering Method

**Qiuhan Gu**



## How to train

* `python pipeline.py`
* `python train.py`

## How to use

> 直接使用

* `cd usage`
* `vim script.py`，删去最后的注释，修改`input_string`为你的代码片段，保存并退出
* `python script.py`

> 调用

* 复制整个`/usage`文件夹至你的代码目录下

* ```python
  from usage import script
  
  input_string="package domain\n\n\nfunc MathPaymentMethodFlag(methods []int) int {\n\tf := 0\n\tfor _, v := range methods {\n\t\tf |= 1 << uint(v-1)\n\t}\n\treturn f\n}\n\n\n\n\nfunc AndPayMethod(payFlag int, method int) bool \n\tf := 1 << uint(method-1)\n\treturn payFlag&f == f\n"
  
  label, probability = script.Cluster().cluster(input_string)
  
  print("The category of the program is（1 for Normal Data, 2 for Anomalous Data）："+ str(label))
  print("Specific probability of 1:2: "+str(probability))
  ```

  
