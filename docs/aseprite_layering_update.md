# Aseprite Layering & Export Update – November 2025

This note captures the current workflow for preparing sprites in Aseprite so the analyser can ingest pixel-perfect trait masks.

## 1. Resize & Baseline Assets
- All PNGs under `Aseperite/all/` (except `lady_099_VQ.png`, which was already complete) have been batch-resized to **24×24** using nearest-neighbour.
- Use `00_Ref_Flattened` as the locked reference layer when checking against the original art.

## 2. Layer Naming Cheatsheet
See `docs/layering_guidelines.md` for the full table. Highlights:

| Slot | Example Layer Names | Notes |
| --- | --- | --- |
| `01_Background_<Pattern>` | `Background_Gradient_Linear`, `Background_Bricks` | Include multi-split backgrounds, candlestick charts, gallery paintings. |
| `02_BackAccessory_<Item>` | `BackAccessory_Halo`, `BackAccessory_Wings_Feathered` | Halos, wing variants, floating logos. |
| `03_Outline` | `Outline_Auto` | Sprite contour only; pupils go with the eyes. |
| `04_Base_Skin_<Tone>` | `Base_Skin_Light`, `Base_Skin_Dark` | Drop all skin pixels here; analyser handles tone naming. |
| `06_Hair_Main_<Style>` | `Hair_Main_Dreadlocks`, `Hair_Main_Updo` | Core hairstyle. |
| `07_Hair_Accessory_<Item>` | `Hair_Accessory_Bow_Large`, `Hair_Accessory_Flower` | Includes bows, clips, flowers; importer maps them to `Hair_Accessory_*`. |
| `07_Hair_Facial_<Type>` | `Hair_Facial_Goatee`, `Hair_Facial_Stubble` | Facial hair variants. |
| `08_Headwear_<Type>` | `Headwear_Cap_Fwd`, `Headwear_BearEars`, `Headwear_CapeHood` | Full hats/hoods/headbands. |
| `09_Headwear_Accent_<Detail>` | `Headwear_Accent_Logo`, `Headwear_Accent_Pom` | Logos, jeweled trims, pom poms. |
| `10_Face_Eyes` | — | Irises/sclera. |
| `11_Face_EyeMakeup` | `EyeMakeup_Eyeshadow`, `EyeMakeup_Eyeliner` | Eyeshadow & eyeliner. |
| `12_Face_Eyes_Laser` | `Eyes_Laser_Green` | Laser/glow overlays. |
| `13_Face_Mouth_<Expression>` | `Face_Mouth_Smile`, `Face_Mouth_Neutral`, `Face_Mouth_Open`, `Face_Mouth_Smirk` | Mouth expressions. |
| `14_Face_Marks` | — | Nose, freckles, dermal marks. |
| `15_Eyewear_<Variant>` | `Eyewear_Sunglasses_Chunky`, `_MidChunky`, `_Thin`, `_UltraThin`, `_SemiOpaque`, `Eyewear_PartyVisor_SemiOpaque` | Covers all thickness and opacity tiers. |
| `16_FaceAccessory_<Item>` | `FaceAccessory_Mask_Medical`, `FaceAccessory_Bandana_Mouth` | Masks, respirators, ninja/balaclava wraps, headphones. |
| `17/18_Face_Implant_*` | — | Cybernetic brow/cheek implants. |
| `19_CL_Mid_Sweater_<Type>` | `CL_Mid_Sweater_TankTop`, `_Turtleneck`, `_Bodysuit`, `_Wetsuit` | All inner/mid tops. |
| `20_CL_Outer_Blazer_<Type>` | `CL_Outer_Blazer_Suit`, `_Blazer`, `_Capelet` | Professional suit tops and similar outer layers. |
| `21_CL_Outer_Coat_<Type>` | `CL_Outer_Coat_Fur`, `_Puffer`, `_CapeHood`, `_LBA`, `_Hoodie` | Heavy outerwear. |
| `22_CL_Scarf_Hood_<Type>` | `CL_Scarf_Hood_Shawl`, `_DetachableHood` | Scarves and detachable hoods. |
| `23_CL_Tie_<Type>` | `CL_Tie_Necktie`, `_Bowtie`, `_Bolo` | Knot-based accessories. |
| `24_CL_PocketAccessory_<Type>` | `CL_PocketAccessory_PocketSquare` | Lapel décor. |
| `25_CL_Bottoms_<Type>` | `CL_Bottoms_Skirt`, `_DressSkirt` | Lower garments. |
| `26_CL_SleeveAccent_<Type>` | `CL_SleeveAccent_Bracelet`, `_Wristwatch` | Wrists/forearms. |
| `29_Jewelry_Earring_<Type>` | `Jewelry_Earring_Stud_Gold`, `_Hoop_Silver`, `_Dangle_Sapphire` | Earring taxonomy. |
| `29_Jewelry_Necklace_<Type>` | `Jewelry_Necklace_Choker_Gold`, `_Chain_Long_Silver`, `_Pendant_Heart` | Necklaces. |
| `30_Prop_Front / 31_Prop_Back` | `Prop_Front_Microphone`, `Prop_Back_Flag` | Fore/back props. |
| `32-35_Smoke_*` | Joints, cigarettes, cigars, holders | Separate plume layer per type. |

## 3. Selection Shortcuts in Aseprite
- **Ctrl/Cmd + click** a layer thumbnail to load its pixels as a selection (great for auditing masks).
- Or use **`Select → Load from Layer → Sprite`**.
- Clear with `Ctrl/Cmd + D`.

## 4. Miscellaneous Notes
- Leave pupils with the eye layers, not the outline.
- Background naming can stay simple—`01_Background` is sufficient—but you can append `_Solid` if it helps you stay organised.
- When in doubt about garment placement, follow the table above so the importer recognises every trait without manual intervention later.

Keep this doc close while layering; once exported, the analyser will read each mask and handle colour naming and trait roll-ups automatically.
