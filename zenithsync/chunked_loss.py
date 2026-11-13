"""Causal LM loss without materialising [sequence, vocabulary] logits.

Gemma 4's vocabulary is 262,144. Transformers' loss path projects every position
through ``lm_head``, upcasts the logits to float32 and only then applies cross
entropy: at the corpus's longest example (24,366 tokens) that is 12.8 GB of bf16
logits, 25.5 GB once upcast, and as much again for the softmax gradient — the
next out-of-memory after attention, on any card this project can rent.

``install_chunked_causal_loss`` replaces the model instance's ``forward`` for
labelled calls only. Positions are processed in fixed slices under activation
checkpointing, so at most one slice's logits exist at a time, forward or
backward; slices with no supervised target are skipped outright. Unlabelled
calls (evaluation logits) go to the original forward unchanged.

The result is the same quantity transformers computes — final-logit softcapping
in the compute dtype, float32 cross entropy, mean over ``labels[:, 1:] != -100``
— accumulated as a float32 sum and divided once. Tests hold it to transformers'
own loss and gradients.
"""

DEFAULT_CHUNK_TOKENS = 1024
_ALLOWED = frozenset({'input_ids', 'attention_mask', 'labels'})


def _chunk_loss(lm_head, softcap, hidden, targets):
    import torch
    logits = lm_head(hidden)
    if softcap is not None:
        logits = torch.tanh(logits / softcap) * softcap
    return torch.nn.functional.cross_entropy(
        logits.float().reshape(-1, logits.shape[-1]), targets.reshape(-1),
        ignore_index=-100, reduction='sum')


def chunked_causal_loss(base, *, input_ids, attention_mask, labels, chunk_tokens=DEFAULT_CHUNK_TOKENS):
    import torch
    from torch.utils.checkpoint import checkpoint
    if type(chunk_tokens) is not int or chunk_tokens <= 0:
        raise ValueError('Positive integer chunk size required')
    if labels.shape != input_ids.shape or labels.ndim != 2 or labels.shape[1] < 2:
        raise ValueError('Labels must match a [batch, sequence>=2] input')
    text = base.config.get_text_config()
    targets = labels[:, 1:]
    supervised = targets != -100
    count = int(supervised.sum().item())
    if count == 0:
        raise ValueError('No supervised next-token target')
    valid = targets[supervised]
    if bool(((valid < 0) | (valid >= text.vocab_size)).any().item()):
        raise ValueError('Label outside the vocabulary')
    hidden = base.model(input_ids=input_ids, attention_mask=attention_mask,
                        use_cache=False).last_hidden_state[:, :-1]
    softcap = text.final_logit_softcapping
    total = None
    for start in range(0, hidden.shape[1], chunk_tokens):
        stop = start + chunk_tokens
        if not bool(supervised[:, start:stop].any().item()):
            continue
        part = checkpoint(_chunk_loss, base.lm_head, softcap, hidden[:, start:stop],
                          targets[:, start:stop], use_reentrant=False)
        total = part if total is None else total + part
    return total / count


def install_chunked_causal_loss(base, *, chunk_tokens=DEFAULT_CHUNK_TOKENS):
    """Route labelled calls on this instance through ``chunked_causal_loss``."""
    from transformers import Gemma4ForCausalLM, Gemma4ForConditionalGeneration
    from transformers.modeling_outputs import CausalLMOutputWithPast
    if type(base) not in (Gemma4ForCausalLM, Gemma4ForConditionalGeneration):
        raise ValueError('Chunked loss is qualified for Gemma 4 causal models only')
    if type(chunk_tokens) is not int or chunk_tokens <= 0:
        raise ValueError('Positive integer chunk size required')
    if getattr(base, '_zenithsync_chunked_loss', None) is not None:
        raise ValueError('Chunked loss already installed')
    original = base.forward

    def forward(**kwargs):
        if set(kwargs) - _ALLOWED or 'input_ids' not in kwargs:
            raise ValueError('Chunked-loss forward accepts only input_ids, attention_mask and labels')
        labels = kwargs.get('labels')
        if labels is None:
            return original(**kwargs)
        loss = chunked_causal_loss(base, input_ids=kwargs['input_ids'],
                                   attention_mask=kwargs.get('attention_mask'),
                                   labels=labels, chunk_tokens=chunk_tokens)
        return CausalLMOutputWithPast(loss=loss, logits=None)

    base.forward = forward
    base._zenithsync_chunked_loss = {'chunk_tokens': chunk_tokens}
    return base
