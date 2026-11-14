"""Sliding-window attention that does window-sized work, not sequence-squared work.

50 of Gemma 4 31B's 60 layers attend only to the previous 1,024 positions, but
the SDPA path hands them a dense ``[seq, seq]`` mask, and the memory-efficient
kernel computes every block of it. The second GPU session measured 3.44 s per
sliding layer, forward and backward, at 24,366 tokens — the same as a full
global layer.

Here a sliding layer splits its queries into blocks of exactly ``window``
positions. Under transformers' rule (``0 <= q - kv < window``) a query in block
``i`` can only see keys in blocks ``i-1`` and ``i``, so each block runs one SDPA
call over ``2 * window`` keys with a fixed band mask. Every block becomes one
batch row of a single fused call: the work is ``seq x 2*window`` instead of
``seq x seq`` — about 8% of it at the corpus's longest example. It is the same
memory-efficient kernel the GPU already qualified, with the same determinism.

Global layers are untouched: they go to transformers' own
``sdpa_attention_forward`` exactly as before.

No mask function is registered for this implementation, so transformers builds
no ``[seq, seq]`` mask at all and passes ``attention_mask=None``. That is
correct only for unpadded or right-padded causal batches — padding at the end
is never visible to a real query under causality — and the chunked-loss entry
point refuses any batch with padding at all, which is stricter than needed.
"""

IMPLEMENTATION = 'zenithsync_sdpa_windowed'
_REFUSED_KWARGS = ('cu_seq_lens_q', 'cu_seq_lens_k', 'max_length_q', 'max_length_k', 's_aux')


def band_mask(window, device):
    """[window, 2*window] bool: query row r may see key column j iff r < j <= r + window."""
    import torch
    rows = torch.arange(window, device=device)[:, None]
    columns = torch.arange(2 * window, device=device)[None, :]
    return (columns > rows) & (columns <= rows + window)


def windowed_attention(query, key, value, *, window, scale):
    """Exact sliding-window causal attention over [batch, heads, seq, dim] tensors.

    Key/value heads must already equal query heads. Returns [batch, heads, seq, dim].
    """
    import torch
    if query.shape != key.shape or key.shape != value.shape or query.ndim != 4:
        raise ValueError('Query, key and value must share one [batch, heads, seq, dim] shape')
    if type(window) is not int or window <= 0:
        raise ValueError('Positive integer window required')
    batch, heads, length, dim = query.shape
    sdpa = torch.nn.functional.scaled_dot_product_attention
    if length <= window:
        # Every visible key is within the window: plain causal attention is exact.
        return sdpa(query, key, value, is_causal=True, scale=scale)
    blocks = -(-length // window)
    padded = blocks * window
    pad_q = (0, 0, 0, padded - length)
    # Keys gain one zero block in front, so block i's window is blocks (i-1, i).
    pad_kv = (0, 0, window, padded - length)
    q = torch.nn.functional.pad(query, pad_q).view(batch, heads, blocks, window, dim)
    k = torch.nn.functional.pad(key, pad_kv).view(batch, heads, blocks + 1, window, dim)
    v = torch.nn.functional.pad(value, pad_kv).view(batch, heads, blocks + 1, window, dim)
    k = torch.cat([k[:, :, :-1], k[:, :, 1:]], dim=3)
    v = torch.cat([v[:, :, :-1], v[:, :, 1:]], dim=3)
    # Fold blocks into the batch dimension: [batch*blocks, heads, rows, dim].
    def fold(tensor):
        return tensor.permute(0, 2, 1, 3, 4).reshape(batch * blocks, heads, tensor.shape[3], dim)
    # Key position of column j in block i is (i-1)*window + j; it must lie in [0, length).
    positions = (torch.arange(blocks, device=query.device)[:, None] - 1) * window \
        + torch.arange(2 * window, device=query.device)[None, :]
    valid = (positions >= 0) & (positions < length)
    mask = band_mask(window, query.device)[None] & valid[:, None, :]
    mask = mask[None].expand(batch, -1, -1, -1).reshape(batch * blocks, 1, window, 2 * window)
    out = sdpa(fold(q), fold(k), fold(v), attn_mask=mask, scale=scale)
    out = out.view(batch, blocks, heads, window, dim).permute(0, 2, 1, 3, 4)
    return out.reshape(batch, heads, padded, dim)[:, :, :length]


def windowed_sdpa_forward(module, query, key, value, attention_mask, dropout=0.0,
                          scaling=None, sliding_window=None, **kwargs):
    """transformers attention interface: windowed for sliding layers, SDPA otherwise."""
    from transformers.integrations.sdpa_attention import repeat_kv, sdpa_attention_forward
    if attention_mask is not None:
        raise ValueError('Windowed attention expects no materialised mask')
    if not getattr(module, 'is_causal', False):
        raise ValueError('Windowed attention supports causal layers only')
    if dropout:
        raise ValueError('Attention dropout is not supported')
    if kwargs.get('output_attentions') or any(kwargs.get(name) is not None for name in _REFUSED_KWARGS):
        raise ValueError('Packed sequences and attention outputs are not supported')
    if sliding_window is None:
        return sdpa_attention_forward(module, query, key, value, None, dropout=0.0,
                                      scaling=scaling, is_causal=True)
    groups = getattr(module, 'num_key_value_groups', 1)
    key, value = repeat_kv(key, groups), repeat_kv(value, groups)
    out = windowed_attention(query, key, value, window=sliding_window, scale=scaling)
    return out.transpose(1, 2).contiguous(), None


def register():
    """Idempotent global registration with transformers' attention interface."""
    from transformers import AttentionInterface
    AttentionInterface.register(IMPLEMENTATION, windowed_sdpa_forward)
    return IMPLEMENTATION
