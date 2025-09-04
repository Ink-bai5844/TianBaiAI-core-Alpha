import json
import sys

def close_script():
    sys.exit()

def SplitMessageinfo(message_info):
    data = json.loads(message_info)
    control_object = data.get('control_object', '')
    control_value = data.get('control_value', -1)
    return control_object, control_value

def PythonSystemIO(control_object, control_value):
    match control_object:
        case "endprocess":
            if control_value == 0:
                print("执行系统操作: 关闭后端进程")
                close_script()
            else:
                print(f"未知的系统操作值: {control_value}")
        case _:
            print(f"未知的控制对象: {control_object}")
    print(f"控制对象: {control_object}, 控制值: {control_value}")
    return 

def domessage(message_type, time, message_info):
    match message_type:
        case "pythonsystemio":
            control_object, control_value = SplitMessageinfo(message_info)
            PythonSystemIO(control_object, control_value)
            return "PythonSystemIO"
        case _:
            return "Default Case"
