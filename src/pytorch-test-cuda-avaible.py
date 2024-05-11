import torch
print("Is cuda available:", torch.cuda.is_available())

import torchvision.ops as ops

boxes = torch.tensor([[10, 15, 30, 35], [20, 25, 40, 45]], dtype=torch.float32)
scores = torch.tensor([0.9, 0.8])
nms_result = ops.nms(boxes, scores, 0.5)
print(nms_result)  # Output indeks kotak yang bertahan setelah NMS
