#!/usr/bin/env python3
"""
Fix SD-piXL to handle when controlnet is disabled (empty list)
"""

from pathlib import Path

def fix_controlnet_logic():
    """Fix LSDS_SDXL_ControlNet_pipeline.py to handle controlnet=[]"""

    pipeline_file = Path("SD-piXL/pipelines/distillation/LSDS_SDXL_ControlNet_pipeline.py")

    if not pipeline_file.exists():
        print(f"❌ File not found: {pipeline_file}")
        return False

    print(f"📝 Reading {pipeline_file}...")
    content = pipeline_file.read_text()

    # Find the problematic section and add a check for empty controlnet
    old_pattern = '''        # Input augmentation
        image_list = [pred_rgb]
        if isinstance(self.controlnet, ControlNetModel):
            image_list.append(controlnet_images)
        elif isinstance(self.controlnet, MultiControlNetModel):
            image_list.extend(controlnet_images)
        image_list_a = self.x_augment_same(image_list, im_size)
        pred_rgb_a = image_list_a[0]
        if isinstance(self.controlnet, ControlNetModel):
            image_a = image_list_a[1]
        elif isinstance(self.controlnet, MultiControlNetModel):
            image_a = image_list_a[1:]'''

    new_pattern = '''        # Input augmentation
        image_list = [pred_rgb]
        if isinstance(self.controlnet, ControlNetModel):
            image_list.append(controlnet_images)
        elif isinstance(self.controlnet, MultiControlNetModel):
            image_list.extend(controlnet_images)
        image_list_a = self.x_augment_same(image_list, im_size)
        pred_rgb_a = image_list_a[0]
        if isinstance(self.controlnet, ControlNetModel):
            image_a = image_list_a[1]
        elif isinstance(self.controlnet, MultiControlNetModel):
            image_a = image_list_a[1:]
        else:
            # No controlnet, skip image preparation
            image_a = None'''

    if old_pattern not in content:
        print("❌ Could not find pattern to patch")
        return False

    content = content.replace(old_pattern, new_pattern)

    # Now fix the second section to handle None
    old_pattern2 = '''        # 4. Prepare image
        if isinstance(self.controlnet, ControlNetModel):
            image = self.prepare_image(
                image=image_a,
                width=im_size,
                height=im_size,
                batch_size=self.batch_size * self.num_images_per_prompt,
                num_images_per_prompt=self.num_images_per_prompt,
                device=self.device,
                dtype=self.controlnet.dtype,
            )
            height, width = image.shape[-2:]
        elif isinstance(self.controlnet, MultiControlNetModel):
            images = []
            for image_ in image_a:
                image_ = self.prepare_image(
                    image=image_,
                    width=im_size,
                    height=im_size,
                    batch_size=self.batch_size * self.num_images_per_prompt,
                    num_images_per_prompt=self.num_images_per_prompt,
                    device=self.device,
                    dtype=self.controlnet.dtype,
                )
                images.append(image_)
            image = images
            height, width = image[0].shape[-2:]
        else:
            assert False'''

    new_pattern2 = '''        # 4. Prepare image
        if isinstance(self.controlnet, ControlNetModel):
            image = self.prepare_image(
                image=image_a,
                width=im_size,
                height=im_size,
                batch_size=self.batch_size * self.num_images_per_prompt,
                num_images_per_prompt=self.num_images_per_prompt,
                device=self.device,
                dtype=self.controlnet.dtype,
            )
            height, width = image.shape[-2:]
        elif isinstance(self.controlnet, MultiControlNetModel):
            images = []
            for image_ in image_a:
                image_ = self.prepare_image(
                    image=image_,
                    width=im_size,
                    height=im_size,
                    batch_size=self.batch_size * self.num_images_per_prompt,
                    num_images_per_prompt=self.num_images_per_prompt,
                    device=self.device,
                    dtype=self.controlnet.dtype,
                )
                images.append(image_)
            image = images
            height, width = image[0].shape[-2:]
        else:
            # No controlnet, skip image preparation
            image = None
            height, width = pred_rgb_a.shape[-2:]'''

    if old_pattern2 not in content:
        print("❌ Could not find second pattern to patch")
        return False

    content = content.replace(old_pattern2, new_pattern2)

    print(f"✅ Writing patched file...")
    pipeline_file.write_text(content)
    print(f"✅ Successfully patched {pipeline_file}!")
    return True


if __name__ == "__main__":
    print("="*80)
    print("🔧 FIX SD-piXL CONTROLNET LOGIC")
    print("="*80)
    print()

    if fix_controlnet_logic():
        print()
        print("✅ ControlNet logic fixed!")
        print()
        print("Now run SD-piXL again")
    else:
        print()
        print("❌ Patch failed!")
        exit(1)
