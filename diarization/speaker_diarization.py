from dotenv import load_dotenv
import os
from pyannote.audio import Pipeline
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

load_dotenv()

pyannote_token = os.getenv('PYANNOTE_TOKEN')

pipeline = Pipeline.from_pretrained(
    'pyannote/speaker-diarization-3.1', use_auth_token=pyannote_token
)

pipeline.to(torch.device('cuda'))
