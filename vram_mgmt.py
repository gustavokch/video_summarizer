import gc
import torch
import subprocess as sp
import os

def clean_vram():
    free_vram = get_gpu_memory()
    if free_vram < 8000:
        clean_vram()
    gc.collect()
    torch.cuda.empty_cache()
    #    del self.model
    #    del self.batched_model
    gc.collect()
    torch.cuda.empty_cache()

def get_gpu_memory():
    command = "nvidia-smi --query-gpu=memory.free --format=csv"
    memory_free_info = sp.check_output(command.split()).decode('ascii').split('\n')[:-1][1:]
    memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
    return int(memory_free_values[0])


        