# Template-following build record

The group-meeting deck follows an institution-branded PPTX owned by the author. The source template is not duplicated in this repository; point the build workflow to the author's local copy.

1. Inspect the source PPTX with the presentation skill's template inspection script.
2. Validate `template-frame-map.json` and prepare `template-starter.pptx` by cloning source slides in mapped order.
3. Run:

```powershell
node scripts/presentations/build_application_deck_full.mjs template-starter.pptx presentations/医学检测具身智能_应用完整版.pptx
```

4. Render every slide, inspect at full size, scan for slide-boundary overflow, and run the template-fidelity check.

The frame map intentionally preserves slides 1–4, uses the source content frame for slides 5–29, and preserves the closing slide as slide 30. New native objects are confined to the content zone below the inherited header.
