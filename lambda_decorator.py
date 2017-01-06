import inspect
import pylambda
import os
import boto3 as boto
import json
from types import ModuleType

class aws_lambda(object):
    def __init__(self, modules, bucket_name):
        self.bucket_name = bucket_name
        try:
            os.mkdir("payload")
        except:
            pass
        with open("payload/requirements.txt", "w") as f:
            for module in modules:
                if type(module) is str:
                    f.write(module + "\n")
                elif type(module) is ModuleType:
                    f.write(module.__name__ + "==" + module.__version__ + "\n")
                else:
                    raise ValueError("decorator arguments must be strings or modules")
    
    def __call__(self, fn):
        with open("payload/"+fn.__name__+".py", "w") as f:
            f.write(inspect.getsource(fn))
        
        pylambda.LambdaDeploy("payload", self.bucket_name, fn.__name__)
        
        def hit_lambda(*args, **kwargs):
            region = kwargs.pop("region", "eu-west-1")
            payload = {"args": args, "kwargs": kwargs}
            name = fn.__name__
            ret = boto.client("lambda", region).invoke(FunctionName=name,
                                                       Payload=json.dumps(payload))
            return ret
        
        return hit_lambda()