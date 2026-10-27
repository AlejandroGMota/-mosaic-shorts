"""Plan render chunks (<=25 s) for all social outputs; print job lines."""
from social import CLIPS, END_CARD
from scenes import DURATION
def chunks(total, n=25.0):
    k = max(1, round(total / n + .49)); step = total / k
    return [(round(i * step * 25) / 25, round((i + 1) * step * 25) / 25) for i in range(k)]
for cid, (a, b, *_ ) in CLIPS.items():
    for i, (s0, s1) in enumerate(chunks(b - a + END_CARD)): print(cid, f"../work/social/{cid}_{i}.mp4", s0, s1)
for i, (s0, s1) in enumerate(chunks(DURATION)): print("square", f"../work/social/square_{i}.mp4", s0, s1)
