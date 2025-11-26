import fs from 'fs/promises';
import path from 'path';
import punkNames from '@/public/punk-names-validated.json';
import VariantReview, { VariantGroup } from './VariantReview';

async function getVariantGroups(): Promise<VariantGroup[]> {
  const projectRoot = path.join(process.cwd(), 'public', 'punks');
  const entries = await fs.readdir(projectRoot);
  const imageFiles = entries.filter(entry => entry.endsWith('.png'));

  const canonicalSet = new Set<string>(punkNames);

  const canonicalByBase = new Map<string, string>();
  for (const name of punkNames) {
    const baseId = name.split('_').slice(0, 2).join('_');
    if (!canonicalByBase.has(baseId)) {
      canonicalByBase.set(baseId, name);
    }
  }

  const variantsByBase = new Map<string, string[]>();
  for (const file of imageFiles) {
    const name = file.replace(/\.png$/i, '');
    const baseId = name.split('_').slice(0, 2).join('_');
    if (canonicalSet.has(name)) {
      continue;
    }
    const bucket = variantsByBase.get(baseId) ?? [];
    bucket.push(name);
    variantsByBase.set(baseId, bucket);
  }

  const groups: VariantGroup[] = [];
  for (const [baseId, variants] of variantsByBase.entries()) {
    variants.sort((a, b) => a.localeCompare(b));
    const canonical = canonicalByBase.get(baseId);
    groups.push({
      baseId,
      canonical: canonical
        ? { name: canonical, src: `/punks/${canonical}.png` }
        : undefined,
      variants: variants.map(name => ({
        name,
        src: `/punks/${name}.png`,
      })),
    });
  }

  groups.sort((a, b) => a.baseId.localeCompare(b.baseId));
  return groups;
}

export default async function VariantReviewPage() {
  const groups = await getVariantGroups();

  return (
    <div className="min-h-screen bg-[#0a0806] text-[#c9a96e]">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <header className="mb-12">
          <p className="text-xs tracking-[0.35em] text-[#c9a96e]/50 uppercase">
            COLLECTION CURATION
          </p>
          <h1 className="serif text-3xl mt-3 text-[#c9a96e]">
            Variant Punk Review
          </h1>
          <p className="mt-4 text-sm text-[#c9a96e]/60 leading-relaxed max-w-3xl">
            Use this panel to inspect alternate renders that exist in the{' '}
            <code className="px-1 py-0.5 bg-black/40 border border-[#c9a96e]/20 text-[11px]">
              public/punks
            </code>{' '}
            directory but are not part of the validated collection. Toggle the
            versions you want to promote into the curated list, then copy or
            download the selection for further processing.
          </p>
        </header>

        <VariantReview groups={groups} />
      </div>
    </div>
  );
}

