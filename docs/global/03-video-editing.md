# Shortening a screen recording

## The rules (the user's, after two failed approaches)

1. Only **still frames** may be trimmed (cut) or held (extended).
2. **Moving frames** may only change playback speed (default 1.0×; at most 1.5× and only if needed).
3. Nothing else: no pointer erasing/redrawing, no blur, no cross-fades.
4. Scene joins must sit **inside still frames**, so both sides are identical and the cut is invisible.

## What failed

- Uniform 2× speed-ups made the mouse pointer move frantically.
- Erasing the real pointer (template matching + inpainting) and drawing a smoothed synthetic one left smudges over text and was judged worse than the original. Do not remove or fake the pointer.
- Cutting at transcript timestamps put joins mid-action (window animations), so a glimpse of the next scene appeared before the cut.

## Method (`tools/motion.py`, `tools/edit_video.py`)

1. Motion per frame = number of pixels whose gray value changed by more than 25 between consecutive frames at 480×266. A frame is "still" at ≤ 8 changed pixels. In this recording 94% of frames were still, so trimming alone removes most of the time.
2. Still runs shorter than 10 frames (0.4 s) are ignored. For each scene, remove frames from the **longest** still runs first (water-filling) down to a floor of 10 frames per run, cutting from the middle of the run.
3. If the scene is still too long, speed up the remaining frames (cap 1.5×) and lengthen the scene instead of exceeding the cap. If the narration is longer than the scene, hold a still frame.
4. Scene length target = narration length + 2 s (+4 s for the last scene); narration starts 0.8 s into the scene.
5. Snap each scene boundary (nominal time from the transcript) to the middle of the nearest still run (≥ 0.4 s within ±12 s).
6. Output by decoding the source once and writing the selected frame indices (no filtering), encode x264 crf 16, copy the video stream when muxing.

## Verification

- Compute changed pixels in ±3 frames around every join (should be ~0) and for every internal trim cut (most are exactly 0; a few pixels of pointer drift are acceptable).
- Note the result: this project had 13 joins with ≤ 4 changed pixels and 321 trim cuts, 278 exactly identical.
