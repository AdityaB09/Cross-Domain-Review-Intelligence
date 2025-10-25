# ml/explain.py
from typing import Dict, Any, List, Tuple
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

class Explainer:
    def __init__(self):
        # load same model as sentiment so explanations line up
        self.tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        self.model.eval()

        # we need gradients
        for p in self.model.parameters():
            p.requires_grad_(True)

    def _forward_with_grads(self, text: str):
        """
        Run model on text using manual embeddings so we can grab grad wrt input embeddings.
        Returns tokens, grads, embeds.
        """
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=False,
        )
        input_ids = enc["input_ids"]          # [1, seq]
        attention_mask = enc["attention_mask"]

        # get embeddings so we can retain grad on them
        emb_layer = self.model.get_input_embeddings()
        inputs_embeds = emb_layer(input_ids)  # [1, seq, hidden]
        inputs_embeds.retain_grad()

        out = self.model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask
        )

        logits = out.logits        # [1,2]
        probs = F.softmax(logits, dim=-1)[0]
        pred_idx = int(torch.argmax(probs).item())
        pred_logit = logits[0, pred_idx]

        # backprop
        self.model.zero_grad()
        pred_logit.backward()

        grads = inputs_embeds.grad.detach().clone()[0]     # [seq, hidden]
        embeds = inputs_embeds.detach().clone()[0]         # [seq, hidden]

        tok_ids = input_ids[0].tolist()
        toks = self.tokenizer.convert_ids_to_tokens(input_ids[0])

        return toks, grads, embeds

    def _grad_x_input_importance(
        self,
        grads: torch.Tensor,
        embeds: torch.Tensor
    ) -> torch.Tensor:
        """
        grads, embeds: [seq, hidden]
        importance = sum(grad * embed) over hidden dim
        normalize to [-1,1]-ish.
        """
        imp = (grads * embeds).sum(dim=-1)  # [seq]
        max_abs = torch.max(torch.abs(imp)).item()
        if max_abs > 0:
            imp = imp / max_abs
        return imp  # [seq] float tensor ~[-1,1]

    def _merge_wordpieces(
        self,
        tokens: List[str],
        importances: List[float]
    ) -> List[Tuple[str,float]]:
        """
        Merge WordPiece sub-tokens back into whole words.
        Example: ['charg', '##ing'] -> ('charging', avg_score)
        Also drop special tokens [CLS]/[SEP].
        """
        merged: List[Tuple[str,float]] = []

        cur_word = ""
        cur_scores: List[float] = []

        for tok, score in zip(tokens, importances):
            if tok.startswith("##"):
                piece = tok[2:]
                cur_word += piece
                cur_scores.append(score)
            else:
                # flush previous
                if cur_word:
                    merged.append((cur_word, sum(cur_scores)/len(cur_scores)))
                # start new
                cur_word = tok
                cur_scores = [score]

        # flush final
        if cur_word:
            merged.append((cur_word, sum(cur_scores)/len(cur_scores)))

        # strip [CLS]/[SEP]
        cleaned: List[Tuple[str,float]] = []
        for w, s in merged:
            if w in ("[CLS]", "[SEP]"):
                continue
            cleaned.append((w, s))

        return cleaned

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Returns:
        {
          "text": text,
          "tokens":[
            {"token":"Camera","attribution":0.1},
            {"token":"sharp","attribution":0.9},
            {"token":"slow","attribution":-0.9},
            ...
          ]
        }
        which matches the shape routes_explain.py already returns. :contentReference[oaicite:14]{index=14}
        """
        toks, grads, embeds = self._forward_with_grads(text)

        imp_tensor = self._grad_x_input_importance(grads, embeds)
        imp_list = imp_tensor.tolist()

        merged = self._merge_wordpieces(toks, imp_list)

        tokens_out: List[Dict[str, Any]] = []
        for w, s in merged:
            tokens_out.append({
                "token": w,
                "attribution": float(round(s, 3)),
            })

        return {
            "text": text,
            "tokens": tokens_out,
        }

# singleton used by routes_explain.py
explainer = Explainer()
