import os

def get_mode_torch() -> str:
    import torch
    if torch.cuda.is_available():
        return "gpu"
    return "cpu"


def get_device_torch() -> str:
    import torch
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_device_name() -> str:
    import torch
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(torch.cuda.current_device())
    return ""
