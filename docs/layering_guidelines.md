# Layering Guidelines for Trait Masks

This document describes the lightweight layer taxonomy we use when exporting sprites from Aseprite. Keeping a consistent ordering and naming scheme makes it easy to ingest the ground-truth masks and let the analyser handle colour naming, coverage, and roll-ups automatically.

## Recommended Layer Order

Prefix each layer with a two-digit index so the stack stays ordered, even if the timeline gets sorted alphabetically. Omit layers that do not apply to a given sprite.

```
00_Ref_Flattened           # Optional locked reference / flattened composite

01_Background              # Full fill, gradients, ambient scenery
02_BackAccessory           # Wings, halos, anything behind the sprite
03_Outline                 # Optional; black contour if kept separate

04_Base_Skin               # All exposed skin pixels
05_Base_Shadows            # Optional darker skin tones / shading

06_Hair_Main               # Primary hair mass
07_Hair_Accessory          # Clips, streaks, highlights (duplicate as needed)

08_Headwear_Main           # Caps (forward/backward), crowns, hoods, animal-ear headbands
09_Headwear_Accents        # Logos, bill trims, gemstones, ear inners

10_Face_Eyes               # Irises & sclera (use Face_Eyes_Laser for glow/beam overlays)
11_Face_EyeMakeup          # Eyeshadow, eyeliner, mascara, false lashes
12_Face_Eyes_Laser         # Laser overlays, glowing pupils, special FX
13_Face_Mouth              # Lips, teeth, cigarettes (if grouped here)
14_Face_Marks              # Nose, freckles, beauty spots, dermal piercings

15_Eyewear_Main            # Glasses frames, visors, lens shapes (e.g., Sunglasses_Chunky, Glasses_Thin)
16_FaceAccessory_Main      # Headphones, face bandanas, respirators, eye patches
17_Face_Implant_Brow       # Cybernetic brow strips, upper-face implants
18_Face_Implant_Cheek      # Cheek-mounted dermal implants, lower-face modules

19_CL_Inner_Shirt          # Tees, dress shirts, undershirts
20_CL_Inner_Vest           # Vests or waistcoats under outerwear
21_CL_Mid_Sweater          # Cardigans, pullovers worn between shirt and coat
22_CL_Outer_Blazer         # Blazers, sport coats, suit jackets
23_CL_Outer_Coat           # Overcoats, trench coats, capes
24_CL_Scarf_Hood           # Scarves, shawls, detachable hoods (top-of-head bandanas go in Headwear)
25_CL_Tie                  # Ties, bowties, bolo ties, ascots
26_CL_PocketAccessory      # Pocket squares, lapel flowers, boutonnieres
27_CL_Bottoms              # Skirts, trousers, belts (optional for 24×24 sprites)
28_CL_SleeveAccent         # Cufflinks, wrist wraps, arm bands
29_Jewelry                 # Earrings, necklaces, piercings

30_Prop_Front              # Items held in front of the sprite
31_Prop_Back               # Items tucked behind but not part of the background

32_Smoke_Joint             # Hand-rolled joints, blunts, hash rolls
33_Smoke_Cigarette         # Filter cigarettes
34_Smoke_Cigar             # Cigars, cigarillos
35_Smoke_Holder            # Cigarette holders, pipes, mouthpieces

```

## Background & Back Accessory Notes
- Capture every region inside `01_Background`, including linear/radial gradients, brick patterns, pinstripes, wave motifs, candlestick charts, gallery paintings, and multi-section colour splits (two, three, or four blocks). Duplicate layers if separate masks help downstream processing.
- Reserve `02_BackAccessory` for elements positioned behind the sprite—halos, all angel-wing variants, floating logos, backdrops, etc.—and suffix them clearly (e.g., `02_BackAccessory_Halo`, `02_BackAccessory_Wings_Feathered`).

## Hair & Facial Hair Notes
- Use `06_Hair_Main` for the primary hairstyle (down, half-up, buns, ponytails, dreadlocks, cornrows, braids, updos, etc.).
- Duplicate `07_Hair_Accessory` for bows (large/small), barrettes, clips, ribbons, coloured streaks, or floral pieces (e.g., Winehouse); name them descriptively such as `07_Hair_Accessory_Bow_Large`. All of these will roll up to `Hair_Accessory_*` traits during import.
- Facial hair (stubble, moustache, goatee, chin strap, soul patch, sideburns) can sit on additional accessory layers like `07_Hair_Accessory_FacialHair_Goatee`, keeping related shading with the same layer.

### Headwear Notes
- **Caps & hats**: keep the entire hat in `08_Headwear_Main`. Add logos, brim trims, or orientation cues (forward/backward) to `09_Headwear_Accents` with suffixes like `_Cap_Fwd_Logo` or `_Cap_Back`.
- **Crowns, tiaras, animal-ear/bear-ear beanies**: place the base band and ears in `08_Headwear_Main`, with jewels, ear inners, LED tips, or pom poms in `09_Headwear_Accents`.
- **Beanies**: simple or pom/puff-top styles stay in `08_Headwear_Main`, with optional pom highlights in `09_Headwear_Accents`.
- **Bandanas**: head-wrapped bandanas/kerchiefs → `08_Headwear_Main`; face-covering bandanas → `16_FaceAccessory_Main`.
- **Hooded coats / LBA coat**: put the hood in `08_Headwear_Main` and the coat body on the appropriate clothing layer.

## Eye, Makeup, and Implant Notes
- `10_Face_Eyes` can contain just the iris/sclera pixel.
- Place eyeliner, eyeshadow, mascara, or glitter on `11_Face_EyeMakeup`.
- Use `12_Face_Eyes_Laser` for glow overlays, green laser beams, or animated effects.
- Eyewear variants (e.g., `Eyewear_Sunglasses_Chunky`, `Eyewear_Glasses_Thin`) belong on `15_Eyewear_Main`.
- Brow-mounted cybernetics → `17_Face_Implant_Brow`; cheek dermal implants → `18_Face_Implant_Cheek`.
- Medical/ninja masks, respirators, balaclavas, or face shields should live on `16_FaceAccessory_Main`.

### Clothing & Jewelry Notes
- Duplicate clothing layers when multiple garments stack; suffix the layer name to describe the garment type:
  - `19_CL_Mid_Sweater_Bandeau`, `_Bralette`, `_TankTop`, `_Tank`, `_Tube`, `_Halter`, `_OneShoulder`, `_Turtleneck`, `_Sweater`, `_Hoodie`, `_Bodysuit`, `_Wetsuit`, `_RashGuard`, `_NinjaSuit`.
  - `20_CL_Outer_Blazer_DressTop` for the upper part of dresses; place the skirt on `27_CL_Bottoms` (optionally named `_DressSkirt`).
  - `21_CL_Outer_Coat_LBA`, `_Trench`, `_Cape`, `_CapeHood`, `_Fur`, `_Puffer`, `_Sweatshirt`, `_Hoodie` for specific outerwear styles.
- Ties/bowties/ascots/bolos → `25_CL_Tie_<Type>`.
- Pocket squares, boutonnieres → `26_CL_PocketAccessory_<Type>`.
- Earrings:
  - Studs → `29_Jewelry_Earring_Stud_<MetalOrGem>` (Gold, Diamond, Silver, etc.).
  - Hoops → `29_Jewelry_Earring_Hoop_<Metal>`.
  - Dangle/drop → `29_Jewelry_Earring_Dangle_<Style>`.
- Necklaces:
  - Chokers → `29_Jewelry_Necklace_Choker_<Metal>`.
  - Chains (long) → `29_Jewelry_Necklace_Chain_Long_<Metal>`.
  - Pendants → `29_Jewelry_Necklace_Pendant_<ShapeOrStone>`.
- Bracelets, watches, arm bands → `28_CL_SleeveAccent_<Type>`.

### Smoking Props
- Hand-rolled joints, hash rolls → `32_Smoke_Joint`.
- Store-bought cigarettes → `33_Smoke_Cigarette`.
- Cigars / cigarillos → `34_Smoke_Cigar`.
- Cigarette holders, pipes, vape mouthpieces → `35_Smoke_Holder`, with the smoke plume drawn on the corresponding smoke layer above.

## Selection & Layer Workflow in Aseprite

1. **Select pixels**  
   - `M` – Marquee, `L` – Lasso, `W` – Magic Wand  
   - Hold `Shift` to add, `Ctrl/Cmd` to subtract from the selection
2. **Create a new layer from selection**  
   - `Ctrl/Cmd+J` – New layer via copy  
   - `Ctrl/Cmd+Shift+J` – New layer via cut (removes pixels from the source layer)
3. **Organise the stack**  
   - Double-click the layer name to rename it  
   - `Ctrl/Cmd+]` / `Ctrl/Cmd+[` to move the layer up or down  
   - Toggle visibility with the eye icon (or `.`)
4. **Repeat** for each trait in the order above.

Consistent naming and ordering across sprites lets the importer map each layer to analyser categories without guesswork, ensuring every pixel has an authoritative owner before colour enrichment and variant generation.

| Layer | Use | Examples / Suffixes |
|---|---|---|
| `01_Background_<Pattern>` | Any backdrop pixel | `Background_Gradient_Linear`, `Background_Gradient_Radial`, `Background_Bricks`, `Background_Pinstripe`, `Background_Waves`, `Background_CandlestickChart`, `Background_GalleryPainting`, `Background_Split_2`, `Background_Split_3`, `Background_Split_4` |
| `02_BackAccessory_<Item>` | Behind-the-sprite elements | `BackAccessory_Halo`, `BackAccessory_Wings_Feathered`, `BackAccessory_Wings_Mechanical`, `BackAccessory_Logos` |
| `03_Outline` | Sprite outline | `Outline_Auto`, `Outline_Manual` |
| `04_Base_Skin_<Tone>` | Base skin pixels | `Base_Skin_Light`, `Base_Skin_Medium`, `Base_Skin_Dark`, `Base_Skin_Glow` |
| `05_Base_Shadows_<Tone>` | Skin shadow overlays | `Base_Shadows_Light`, `Base_Shadows_Medium`, `Base_Shadows_Dark` |
| `06_Hair_Main_<Style>` | Core hairstyle | `Hair_Main_Down`, `Hair_Main_HalfUp`, `Hair_Main_Ponytail`, `Hair_Main_Buns`, `Hair_Main_Dreadlocks`, `Hair_Main_Cornrows`, `Hair_Main_Braids`, `Hair_Main_Updo` |
| `07_Hair_Accessory_<Item>` | Bows/clips/etc. | `Hair_Accessory_Bow_Large`, `Hair_Accessory_Bow_Small`, `Hair_Accessory_Clip`, `Hair_Accessory_Flower`, `Hair_Accessory_Streak`, `Hair_Accessory_Barrettes` |
| `07_Hair_Facial_<Type>` | Facial hair | `Hair_Facial_Stubble`, `Hair_Facial_Moustache`, `Hair_Facial_Goatee`, `Hair_Facial_Chinstrap`, `Hair_Facial_SoulPatch`, `Hair_Facial_Sideburns` |
| `08_Headwear_<Type>` | Hats/headbands | `Headwear_Cap_Fwd`, `Headwear_Cap_Back`, `Headwear_Beanie_Simple`, `Headwear_Beanie_Puff`, `Headwear_BearEars`, `Headwear_BucketHat`, `Headwear_Beret`, `Headwear_Tiara`, `Headwear_Crown`, `Headwear_CapeHood` |
| `09_Headwear_Accent_<Detail>` | Logos or trims | `Headwear_Accent_Logo`, `Headwear_Accent_BrimTrim`, `Headwear_Accent_Jewels`, `Headwear_Accent_Pom`, `Headwear_Accent_EarInner` |
| `10_Face_Eyes` | Iris + sclera | — |
| `11_Face_EyeMakeup` | Eye makeup | `EyeMakeup_Eyeshadow`, `EyeMakeup_Eyeliner`, `EyeMakeup_Mascara` |
| `12_Face_Eyes_Laser` | Laser/glow overlays | `Eyes_Laser_Green`, `Eyes_Laser_BlueGlow` |
| `13_Face_Mouth_<Expression>` | Lips/teeth | `Face_Mouth_Smile`, `Face_Mouth_Neutral`, `Face_Mouth_Open`, `Face_Mouth_Smirk` |
| `14_Face_Marks` | Nose/freckles/etc. | — |
| `15_Eyewear_<Variant>` | Glasses/visors | `Eyewear_Sunglasses_Chunky`, `Eyewear_Sunglasses_MidChunky`, `Eyewear_Sunglasses_Thin`, `Eyewear_Sunglasses_UltraThin`, `Eyewear_Sunglasses_SemiOpaque`, `Eyewear_Glasses_Chunky`, `Eyewear_Glasses_MidChunky`, `Eyewear_Glasses_Thin`, `Eyewear_Glasses_UltraThin`, `Eyewear_PartyVisor_SemiOpaque`, `Eyewear_Visor` |
| `16_FaceAccessory_<Item>` | Masks/bandanas | `FaceAccessory_Mask_Medical`, `FaceAccessory_Mask_Ninja`, `FaceAccessory_Bandana_Mouth`, `FaceAccessory_Balaclava` |
| `17_Face_Implant_Brow` | Brow implants | `Face_Implant_Brow_LED` |
| `18_Face_Implant_Cheek` | Cheek implants | `Face_Implant_Cheek_Dermal` |
| `19_CL_Mid_Sweater_<Type>` | Mid layer (includes tops) | `CL_Mid_Sweater_Bandeau`, `_Bralette`, `_TankTop`, `_Tank`, `_Tube`, `_Halter`, `_OneShoulder`, `_Turtleneck`, `_Sweater`, `_Hoodie`, `_Bodysuit`, `_Wetsuit`, `_RashGuard`, `_NinjaSuit` |
| `20_CL_Outer_Blazer_<Type>` | Light outer layer | `CL_Outer_Blazer_DressTop`, `_Blazer`, `_Suit`, `_Cardigan`, `_Capelet` |
| `21_CL_Outer_Coat_<Type>` | Coats & jackets | `CL_Outer_Coat_LBA`, `_Trench`, `_Cape`, `_CapeHood`, `_Fur`, `_Puffer`, `_Coat`, `_Jacket` |
| `22_CL_Scarf_Hood_<Type>` | Scarves & detachable hoods | `CL_Scarf_Hood_Scarf`, `_Shawl`, `_DetachableHood` |
| `23_CL_Tie_<Type>` | Neckties | `CL_Tie_Necktie`, `_Bowtie`, `_Ascot`, `_Bolo` |
| `24_CL_PocketAccessory_<Type>` | Lapel accessories | `CL_PocketAccessory_PocketSquare`, `_Boutonniere` |
| `25_CL_Bottoms_<Type>` | Lower garments | `CL_Bottoms_Skirt`, `_Trousers`, `_Shorts`, `_DressSkirt` |
| `26_CL_SleeveAccent_<Type>` | Wrist/arm accessories | `CL_SleeveAccent_Bracelet`, `_Wristwatch`, `_ArmBand` |
| `29_Jewelry_Earring_<Type>` | Earrings | `Jewelry_Earring_Stud_Gold`, `_Stud_Diamond`, `_Hoop_Silver`, `_Dangle_Sapphire` |
| `29_Jewelry_Necklace_<Type>` | Necklaces | `Jewelry_Necklace_Choker_Gold`, `_Chain_Long_Silver`, `_Pendant_Heart` |
| `30_Prop_Front` | Props held in front | `Prop_Front_Microphone`, `Prop_Front_Cane` |
| `31_Prop_Back` | Props tucked behind | `Prop_Back_Guitar`, `Prop_Back_Flag` |
| `32_Smoke_Joint` | Joints/blunts | — |
| `33_Smoke_Cigarette` | Cigarettes | — |
| `34_Smoke_Cigar` | Cigars/cigarillos | — |
| `35_Smoke_Holder` | Holders/pipes | `Smoke_Holder_CigaretteHolder`, `Smoke_Holder_Pipe`, `Smoke_Holder_Vape` |

