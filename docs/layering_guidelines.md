# Layering Guidelines for Trait Masks

This document describes the lightweight layer taxonomy we use when exporting sprites from Aseprite. Keeping a consistent ordering and naming scheme makes it easy to ingest the ground-truth masks and let the analyser handle colour naming, coverage, and roll-ups automatically.

## Recommended Layer Order

Use the table below as the source of truth. Follow the numbered prefixes and suffix conventions when building Aseprite layers; omit layers that do not apply to a sprite.

## Background & Back Accessory Notes
- Capture every region inside `01_Background`, including linear/radial gradients, brick patterns, pinstripes, wave motifs, candlestick charts, gallery paintings, and multi-section colour splits (two, three, or four blocks). Duplicate layers if separate masks help downstream processing.
- Reserve `02_BackAccessory` for elements positioned behind the sprite—halos, all angel-wing variants, floating logos, backdrops, etc.—and suffix them clearly (e.g., `02_BackAccessory_Halo`, `02_BackAccessory_Wings_Feathered`, `02_BackAccessory_Logo_AbsXyz`).

## Hair & Facial Hair Notes
- Use `06_Hair_Main` for the primary hairstyle (down, half-up, buns, ponytails, dreadlocks, cornrows, braids, updos, etc.).
- Duplicate `07_Hair_Accessory` for bows (large/small), barrettes, clips, ribbons, coloured streaks, or floral pieces (e.g., Winehouse); name them descriptively such as `07_Hair_Accessory_Bow_Large`. All of these will roll up to `Hair_Accessory_*` traits during import.
- Facial hair (stubble, moustache, goatee, chin strap, soul patch, sideburns, beards—short/long/full) sits on `07_Hair_Facial_<Type>`; match the name to what you see (e.g., `Hair_Facial_Stubble`, `Hair_Facial_Moustache`, `Hair_Facial_Goatee`, `Hair_Facial_Beard_Short`, `Hair_Facial_Beard_Long`).
- Bandanas and athletic wraps can use `07_Hair_Accessory_Band` or for tied styles `07_Hair_Accessory_Bandana`.
- If a “mask” is part of a fused ninja cowl, keep it on `08_Headwear_CapeHood`. Only split a separate mask layer when it’s detachable.

### Headwear Notes
- **Caps & hats**: keep the entire hat in `08_Headwear_Main`. Add logos, brim trims, or orientation cues (forward/backward) to `09_Headwear_Accents` with suffixes like `_Cap_Fwd_Logo` or `_Cap_Back`.
- **Crowns, tiaras, animal-ear/bear-ear beanies**: place the base band and ears in `08_Headwear_Main`, with jewels, ear inners, LED tips, or pom poms in `09_Headwear_Accents`. Use `Headwear_Crown_Flower` for full floral crowns.
- **Beanies**: simple or pom/puff-top styles stay in `08_Headwear_Main`, with optional pom highlights in `09_Headwear_Accents`.
- **Bandanas**: head-wrapped bandanas/kerchiefs → `08_Headwear_Main`; face-covering bandanas → `16_FaceAccessory_Main`.
- **Ninja cowls**: if the face cover is fused to the hood, keep the whole cowl on `08_Headwear_CapeHood`; only split a mask layer when it’s a detachable panel.
- **Hooded coats / LBA coat**: put the hood in `08_Headwear_Main` and the coat body on the appropriate clothing layer.

## Eye, Makeup, and Implant Notes
- `10_Face_Eyes` can contain just the iris/sclera pixel.
- Place eyeliner, eyeshadow, mascara, or glitter on `11_Face_EyeMakeup`.
- Use `12_Face_Eyes_Laser` for glow overlays, green laser beams, or animated effects.
- Eyewear variants (e.g., `Eyewear_Sunglasses_Chunky`, `Eyewear_Glasses_Thin`) belong on `15_Eyewear_Main`.
- Brow-mounted cybernetics → `17_Face_Implant_Brow` (e.g., `_LED`, `_Ocular`); cheek dermal implants → `18_Face_Implant_Cheek`.
- Medical/ninja masks, respirators, balaclavas, or face shields should live on `16_FaceAccessory_Main`.

### Clothing & Jewelry Notes
- Duplicate clothing layers when multiple garments stack; suffix the layer name to describe the garment type:
  - `19_CL_Mid_Sweater_Bandeau`, `_Bralette`, `_Tank`, `_Tube`, `_Halter`, `_OneShoulder`, `_Turtleneck`, `_Sweater`, `_Hoodie`, `_Blouse`, `_Bodysuit`, `_Wetsuit`, `_RashGuard`, `_NinjaSuit`.
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
| `01_Background_<Pattern>` | Any backdrop pixel | `Background_Brick`, `Background_Gradient_Linear`, `Background_Gradient_Linear_Diagonal`, `Background_Gradient_Linear_Multi`, `Background_Gradient_Radial`, `Background_Pinstripe`, `Background_Waves`, `Background_Waves_Split_3`, `Background_Waves_Split_4`, `Background_CandlestickChart`, `Background_GalleryPainting`, `Background_Split_2`, `Background_Split_3`, `Background_Split_3_Side`, `Background_Split_4` |
| `02_BackAccessory_<Item>` | Behind-the-sprite elements | `BackAccessory_Halo`, `BackAccessory_Wings_Feathered`, `BackAccessory_Wings_Angel`, `BackAccessory_Wings_Fairy`, `BackAccessory_Wings_Mechanical`, `BackAccessory_Chart_Candlestick`, `BackAccessory_Logos` |
| `03_Outline` | Sprite outline | `Outline_Auto`, `Outline_Manual` |
| `04_Base_Skin` | Base skin pixels | Place all visible skin here (ears, elf ears, tails; colour handled later) |
| `05_Base_Shadows_<Tone>` | Skin shadow overlays | `Base_Shadows_Light`, `Base_Shadows_Medium`, `Base_Shadows_Dark`, `Base_Shadows_Pale` |
| `06_Hair_Main_<Style>` | Core hairstyle | `Hair_Main_Down`, `Hair_Main_Down_Wavy`, `Hair_Main_Down_Curly`, `Hair_Main_Down_Afro`, `Hair_Main_Down_Bob`, `Hair_Main_Down_Men_Layered`, `Hair_Main_HalfUp`, `Hair_Main_HalfUp_CatEarBuns`, `Hair_Main_Ponytail`, `Hair_Main_Ponytail_Side`, `Hair_Main_Ponytail_Long`, `Hair_Main_Buns`, `Hair_Main_Bun_Low`, `Hair_Main_Undercut_LongTop`, `Hair_Main_Undercut_LongTop_Wavy`, `Hair_Main_Buzz`, `Hair_Main_Buzz_Fade`, `Hair_Main_Buzz_Taper`, `Hair_Main_Buzz_FlatTop`, `Hair_Main_Buzz_ShavedSides`, `Hair_Main_Buzz_Sideburns`, `Hair_Main_Dreadlocks`, `Hair_Main_Cornrows`, `Hair_Main_Braids`, `Hair_Main_SlickedBack`, `Hair_Main_SlickedBack_Curls`, `Hair_Main_Updo`, `Hair_Main_Updo_Medical`, `Hair_Main_Fade_Curls` |
| `07_Hair_Accessory_<Item>` | Bows/clips/etc. | `Hair_Accessory_Bow_Large`, `Hair_Accessory_Bow_Small`, `Hair_Accessory_Clip`, `Hair_Accessory_Flower`, `Hair_Accessory_Flower_Daisy`, `Hair_Accessory_Streak`, `Hair_Accessory_Barrettes`, `Hair_Accessory_Band`, `Hair_Accessory_Beads`, `Hair_Accessory_Wrap`, `Hair_Accessory_Antenna`, `Hair_Accessory_CatEarBuns`, `Hair_Accessory_CatEarHeadband`, `Hair_Accessory_Glasses_OnHead`, `Hair_Accessory_Bandana`, `Hair_Accessory_Scarf_Turban`, `Hair_Accessory_Goggles_OnHead` |
| `07_Hair_Facial_<Type>` | Facial hair | `Hair_Facial_Stubble`, `Hair_Facial_Moustache`, `Hair_Facial_Moustache_Long`, `Hair_Facial_Goatee`, `Hair_Facial_Chinstrap`, `Hair_Facial_Chinstrap_Beard`, `Hair_Facial_Beard_Short`, `Hair_Facial_Beard_Long`, `Hair_Facial_Beard_Full`, `Hair_Facial_SoulPatch`, `Hair_Facial_SoulPatch_Thin`, `Hair_Facial_Sideburns`, `Hair_Facial_Shadow` |
| `08_Headwear_<Type>` | Hats/headbands | `Headwear_Cap_Fwd`, `Headwear_Cap_Fwd_Patterned`, `Headwear_Cap_Back`, `Headwear_Beanie_Simple`, `Headwear_Beanie_Rolled`, `Headwear_Beanie_Puff`, `Headwear_BearEars`, `Headwear_CatEars`, `Headwear_DogEars`, `Headwear_BucketHat`, `Headwear_BucketHat_Patterned`, `Headwear_TopHat`, `Headwear_Fedora`, `Headwear_Cowboy`, `Headwear_PartyHat`, `Headwear_Jester`, `Headwear_Wizard`, `Headwear_Wig`, `Headwear_Wig_Bow`, `Headwear_Beret`, `Headwear_Tiara`, `Headwear_Crown`, `Headwear_CapeHood` |
| `09_Headwear_Accent_<Detail>` | Logos or trims | `Headwear_Accent_Logo`, `Headwear_Accent_BrimTrim`, `Headwear_Accent_Jewels`, `Headwear_Accent_Pom`, `Headwear_Accent_EarInner` |
| `10_Face_Eyes` | Iris + sclera | — |
| `11_Face_EyeMakeup` | Eye makeup | `EyeMakeup_Eyeshadow`, `EyeMakeup_Eyeliner`, `EyeMakeup_Mascara` |
| `12_Face_Eyes_Laser` | Laser/glow overlays | `Eyes_Laser_Green`, `Eyes_Laser_BlueGlow` |
| `13_Face_Mouth_<Expression>` | Lips/teeth | `Face_Mouth_Smile`, `Face_Mouth_Neutral`, `Face_Mouth_Open`, `Face_Mouth_Smirk` |
| `14_Face_Marks_<Detail>` | Nose/freckles/etc. | `Face_Marks_Nose`, `Face_Marks_Freckles`, `Face_Marks_BeautySpot`, `Face_Marks_DermalPiercing`, `Face_Marks_FacePaint`, `Face_Marks_Tattoo`, `Face_Marks_Bindi` |
| `15_Eyewear_<Variant>` | Glasses/visors | `Eyewear_Sunglasses_Chunky`, `Eyewear_Sunglasses_Chunky_Long`, `Eyewear_Sunglasses_Chunky_Extra`, `Eyewear_Sunglasses_MidChunky`, `Eyewear_Sunglasses_Medium`, `Eyewear_Sunglasses_Thin`, `Eyewear_Sunglasses_Thin_Semi`, `Eyewear_Sunglasses_Thin_Tall`, `Eyewear_Sunglasses_UltraThin`, `Eyewear_Sunglasses_UltraThin_BigLens`, `Eyewear_Sunglasses_SemiOpaque`, `Eyewear_Glasses_Chunky`, `Eyewear_Glasses_MidChunky`, `Eyewear_Glasses_Thin`, `Eyewear_Glasses_Thin_Rimless`, `Eyewear_Glasses_UltraThin`, `Eyewear_Glasses_Medical_Long`, `Eyewear_PartyVisor_SemiOpaque`, `Eyewear_Visor` |
| `16_FaceAccessory_<Item>` | Masks/bandanas | `FaceAccessory_Mask_Medical`, `FaceAccessory_Mask_Ninja`, `FaceAccessory_Bandana_Mouth`, `FaceAccessory_Balaclava`, `FaceAccessory_Earbud_Left`, `FaceAccessory_Earbud_Right` |
| `17_Face_Implant_Brow` | Brow implants | `Face_Implant_Brow_LED` |
| `18_Face_Implant_Cheek` | Cheek implants | `Face_Implant_Cheek_Dermal` |
| `19_CL_Mid_Sweater_<Type>` | Mid layer (includes tops) | `CL_Mid_Sweater_Bandeau`, `_Bralette`, `_Tank`, `_Tube`, `_Halter`, `_OneShoulder`, `_Turtleneck`, `_Turtleneck_Slim`, `_Sweater`, `_Sweater_VNeck`, `_Sweater_MockNeck`, `_Sweater_VNeck_Professional`, `_Sweater_Pullover`, `_Hoodie`, `_Hoodie_Sport`, `_Blouse`, `_Blouse_PeterPan`, `_DressShirt`, `_Kurta`, `_Dashiki`, `_Bodysuit`, `_Vest`, `_Blazer_Tee`, `_Jersey_Baseball`, `_Tuxedo_Shirt`, `_Ruffled_Shirt`, `_Dress_Fairy`, `_Polo`, `_Macbook_Tee`, `_Festival_Top`, `_CropTop`, `_Wetsuit`, `_RashGuard`, `_NinjaSuit` |
| `20_CL_Outer_Blazer_<Type>` | Light outer layer | `CL_Outer_Blazer_DressTop`, `_Blazer`, `_Suit`, `_Cardigan`, `_Capelet` |
| `21_CL_Outer_Coat_<Type>` | Coats & jackets | `CL_Outer_Coat_LBA`, `_Trench`, `_Cape`, `_CapeHood`, `_Fur`, `_Puffer`, `_Coat`, `_Jacket`, `_Lab`, `_Overalls` |
| `22_CL_Scarf_Hood_<Type>` | Scarves & detachable hoods | `CL_Scarf_Hood_Scarf`, `_Scarf_Crochet`, `_Shawl`, `_DetachableHood` |
| `23_CL_Tie_<Type>` | Neckties | `CL_Tie_Necktie`, `_Bowtie`, `_Ascot`, `_Bolo` |
| `24_CL_PocketAccessory_<Type>` | Lapel accessories | `CL_PocketAccessory_PocketSquare`, `_Boutonniere` |
| `25_CL_Bottoms_<Type>` | Lower garments | `CL_Bottoms_Skirt`, `_Trousers`, `_Shorts`, `_DressSkirt` |
| `26_CL_SleeveAccent_<Type>` | Wrist/arm accessories | `CL_SleeveAccent_Bracelet`, `_Wristwatch`, `_ArmBand` |
| `29_Jewelry_Earring_<Type>` | Earrings | `Jewelry_Earring_Stud_Gold`, `_Stud_Silver`, `_Stud_Diamond`, `_Stud_Emerald`, `_Stud_Pearl`, `_Hoop_Gold`, `_Hoop_Gold_Large`, `_Hoop_Gold_Double`, `_Hoop_Gold_Huggie`, `_Hoop_Silver`, `_Hoop_Silver_Large`, `_Hoop_Silver_Hybrid`, `_Hoop_Small_Gold`, `_Hoop_Plane_Gold`, `_Dangle_Gold`, `_Dangle_Silver`, `_Dangle_Diamond`, `_Dangle_HoopHybrid`, `_Hoop_Hybrid_Gold` |
| `29_Jewelry_Necklace_<Type>` | Necklaces | `Jewelry_Necklace_Choker_Gold`, `_Choker_Silver`, `_Choker_Beaded`, `_Choker_PearlDiamond`, `_Choker_OrnateBlack`, `_Choker_Ribbon`, `_Chain_Gold`, `_Chain_Silver`, `_Chain_Beaded`, `_Chain_Long_Gold`, `_Chain_Wide_Gold`, `_Chain_Pearl`, `_Chain_Pearl_Long`, `_Chain_Dark`, `_Chain_Dark_Long`, `_Pendant_Gold`, `_Pendant_Silver`, `_Pendant_Diamond`, `_Pendant_Triangle`, `_Pendant_Bead` |
| `30_Prop_Front` | Props held in front | `Prop_Front_Microphone`, `Prop_Front_Cane` |
| `31_Prop_Back` | Props tucked behind | `Prop_Back_Guitar`, `Prop_Back_Flag` |
| `32_Smoke_Joint` | Joints/blunts | — |
| `33_Smoke_Cigarette` | Cigarettes | — |
| `34_Smoke_Cigar` | Cigars/cigarillos | — |
| `35_Smoke_Holder` | Holders/pipes | `Smoke_Holder_CigaretteHolder`, `Smoke_Holder_Pipe`, `Smoke_Holder_Vape` |

