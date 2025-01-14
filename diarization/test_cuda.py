'''Модуль для проверки доступности CUDA.'''

import torch
print(torch.__version__)
print(torch.cuda.is_available())
