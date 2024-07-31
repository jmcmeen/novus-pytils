import torch
from PIL import Image
import open_clip

class OpenClip:
    def __init__(self, model_name: str = 'ViT-B-32', pretrained: str = 'laion2b_s34b_b79k') -> None:
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained)
        self.model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active
        self.tokenizer = open_clip.get_tokenizer(model_name)

    def get_image_features(self, image_path: str, tokens: list, device: str = 'cuda', ) -> torch.Tensor:
        text = self.tokenizer(tokens)

        with torch.no_grad(), torch.autocast(device):
            image = self.preprocess(Image.open(image_path)).unsqueeze(0)

            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(text)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            return (100 *image_features @ text_features.T).softmax(dim=-1)

