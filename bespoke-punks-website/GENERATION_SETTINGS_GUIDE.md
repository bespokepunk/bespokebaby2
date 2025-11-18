# Image Generation Settings Guide

## 🎨 FREEPIK FLUX 1.1 SETTINGS

### Required Settings:
- **Model:** Flux 1.1
- **Aspect Ratio:** 16:9 (Landscape)
- **Quality:** High
- **Style:** Keep blank or "Miniature diorama"

### CRITICAL - Negative Prompt Field:
```
people, humans, person, man, woman, child, figure, character, face, portrait, body, hands, arms, legs, feet, eyes, nose, mouth, humanoid, anthropomorphic, realistic person, cartoon character, anime character, silhouette of person, shadow of person, human shadow, human silhouette, statue of person, mannequin, doll, action figure
```

### How to Use:
1. Copy one of the EPIC prompts from `EPIC_PROMPTS_67_FIXED.md`
2. Paste into Freepik main prompt field
3. Copy the negative prompt above into the "Negative Prompt" field
4. Set Aspect Ratio to 16:9
5. Select Flux 1.1 model
6. Generate!

---

## 🎨 MIDJOURNEY SETTINGS

### Command Format:
```
/imagine [PROMPT] --no people, humans, figures, characters, faces, portraits, bodies, person, man, woman, child, humanoid, silhouette, statue, mannequin --ar 16:9 --v 6.1 --style raw
```

### Parameters Explained:
- `--no` = Negative prompt (what to exclude)
- `--ar 16:9` = Aspect ratio (landscape)
- `--v 6.1` = Midjourney version 6.1
- `--style raw` = Less stylization, more literal prompt interpretation

### Alternative Settings to Try:
```
--v 6.1 --style raw --s 50
```
(Lower stylization value makes it follow prompt more literally)

OR

```
--v 6.1 --q 2
```
(Higher quality rendering)

### How to Use:
1. Copy one of the EPIC prompts from `EPIC_PROMPTS_67_FIXED.md`
2. Type `/imagine` in Midjourney
3. Paste prompt
4. Add parameters: `--no people, humans, figures, characters, faces, portraits, bodies, person, man, woman, child, humanoid, silhouette, statue, mannequin --ar 16:9 --v 6.1 --style raw`
5. Press Enter!

---

## 📋 EXAMPLE USAGE

### FREEPIK Example:

**Main Prompt:**
```
Miniature presidential treasury vault diorama bathed in electric lime green atmosphere with glowing dollar sign neon, tiny pixel sunglasses resting on towering stacks of handcrafted miniature currency bills, massive floating Bitcoin symbols creating cascading crypto light with bright green and gold reflections, sleek vault surfaces with George Washington engravings and founding father motifs, scattered cash bundles and digital currency symbols in vivid greens and golds, atmospheric haze with deal-with-it meme energy glow, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with heavy blur making any distant elements completely abstract and out of focus, dream-logic scale where Bitcoin symbols are entire planets of wealth, liminal space between federal reserve and crypto future, shadow puppet theater depth with layered currency silhouettes, folkloric tale of the meme economist, mythological shadow play of founding fathers meets digital revolution, ancient legend of old money embracing new technology, ethereal ghostly lime green glow pulsing with golden currency energy, small-scale treasury magic with visible handbuilt bill textures and pixel sunglasses details, handcrafted crypto meme aesthetic, abstract heavily stylized abstract only, no realism, no realistic faces or characters, abstract atmospheric world only, tilt-shift currency, 16:9
```

**Negative Prompt:**
```
people, humans, person, man, woman, child, figure, character, face, portrait, body, hands, arms, legs, feet, eyes, nose, mouth, humanoid, anthropomorphic, realistic person, cartoon character, anime character, silhouette of person, shadow of person, human shadow, human silhouette, statue of person, mannequin, doll, action figure
```

**Settings:**
- Model: Flux 1.1
- Aspect Ratio: 16:9
- Quality: High

---

### MIDJOURNEY Example:

```
/imagine Miniature presidential treasury vault diorama bathed in electric lime green atmosphere with glowing dollar sign neon, tiny pixel sunglasses resting on towering stacks of handcrafted miniature currency bills, massive floating Bitcoin symbols creating cascading crypto light with bright green and gold reflections, sleek vault surfaces with George Washington engravings and founding father motifs, scattered cash bundles and digital currency symbols in vivid greens and golds, atmospheric haze with deal-with-it meme energy glow, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with heavy blur making any distant elements completely abstract and out of focus, dream-logic scale where Bitcoin symbols are entire planets of wealth, liminal space between federal reserve and crypto future, shadow puppet theater depth with layered currency silhouettes, folkloric tale of the meme economist, mythological shadow play of founding fathers meets digital revolution, ancient legend of old money embracing new technology, ethereal ghostly lime green glow pulsing with golden currency energy, small-scale treasury magic with visible handbuilt bill textures and pixel sunglasses details, handcrafted crypto meme aesthetic, abstract heavily stylized abstract only, no realism, no realistic faces or characters, abstract atmospheric world only, tilt-shift currency, 16:9 --no people, humans, figures, characters, faces, portraits, bodies, person, man, woman, child, humanoid, silhouette, statue, mannequin --ar 16:9 --v 6.1 --style raw
```

---

## ⚠️ TROUBLESHOOTING

### If Figures STILL Appear in Freepik:
1. Add MORE words to negative prompt:
   ```
   people, humans, person, man, woman, child, figure, character, face, portrait, body, hands, arms, legs, feet, eyes, nose, mouth, humanoid, anthropomorphic, realistic person, cartoon character, anime character, silhouette of person, shadow of person, human shadow, human silhouette, statue of person, mannequin, doll, action figure, bust, head, torso, human form, human shape, person shape, character design, human anatomy
   ```

2. Try adding to main prompt:
   - "environment ONLY"
   - "ZERO human presence"
   - "objects and atmosphere exclusively"

### If Figures STILL Appear in Midjourney:
1. Increase `--no` list:
   ```
   --no people, humans, figures, characters, faces, portraits, bodies, person, man, woman, child, humanoid, silhouette, statue, mannequin, bust, head, anime, cartoon character, human form, anthropomorphic, doll, action figure
   ```

2. Try different style parameter:
   ```
   --style raw --s 0
   ```
   (Completely literal interpretation)

3. Try older model version:
   ```
   --v 6 --style raw
   ```

---

## 🎯 BEST PRACTICES

### For Freepik:
- ✅ ALWAYS fill the Negative Prompt field
- ✅ Use Flux 1.1 model
- ✅ Keep prompts focused on objects, atmosphere, and environment
- ✅ Generate 4 variations and pick the best one

### For Midjourney:
- ✅ ALWAYS use `--no` parameter with extensive list
- ✅ Use `--v 6.1` or `--v 6`
- ✅ Use `--style raw` for literal interpretation
- ✅ Use `--ar 16:9` for landscape
- ✅ Generate with different `--seed` values if needed for variety

---

## 📁 FILE NAMING

Save generated images as:
```
/public/punk-worlds/{punk_name}WORLD.png
```

Examples:
- `lady_099_VQWORLD.png`
- `lad_002_cashWORLD.png`
- `lady_096_yuriWORLD.png`

---

## ✅ CHECKLIST BEFORE GENERATING

- [ ] Copied full prompt from `EPIC_PROMPTS_67_FIXED.md`
- [ ] Filled negative prompt field (Freepik) OR added `--no` parameter (Midjourney)
- [ ] Set aspect ratio to 16:9
- [ ] Selected Flux 1.1 (Freepik) OR set `--v 6.1` (Midjourney)
- [ ] Double-checked prompt includes "no human figures" multiple times
- [ ] Ready to generate!
