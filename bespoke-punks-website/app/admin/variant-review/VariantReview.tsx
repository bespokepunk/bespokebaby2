'use client';

import { useMemo, useState } from 'react';

type VariantInfo = {
  name: string;
  src: string;
};

export type VariantGroup = {
  baseId: string;
  canonical?: VariantInfo;
  variants: VariantInfo[];
};

type Props = {
  groups: VariantGroup[];
};

export default function VariantReview({ groups }: Props) {
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [removedCanon, setRemovedCanon] = useState<Record<string, boolean>>({});
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedVariants = useMemo(
    () =>
      groups.flatMap(group =>
        group.variants.filter(variant => selected[variant.name])
      ),
    [groups, selected]
  );

  const removedCanonicals = useMemo(
    () =>
      groups.flatMap(group =>
        group.canonical && removedCanon[group.canonical.name] ? [group.canonical] : []
      ),
    [groups, removedCanon]
  );

  const toggleVariant = (variantName: string) => {
    setStatusMessage(null);
    setSelected(prev => ({
      ...prev,
      [variantName]: !prev[variantName],
    }));
  };

  const toggleCanonical = (canonicalName: string) => {
    setStatusMessage(null);
    setRemovedCanon(prev => ({
      ...prev,
      [canonicalName]: !prev[canonicalName],
    }));
  };

  const handleSelectAll = (group: VariantGroup) => {
    setStatusMessage(null);
    setSelected(prev => {
      const next = { ...prev };
      for (const variant of group.variants) {
        next[variant.name] = true;
      }
      return next;
    });
  };

  const handleClearGroup = (group: VariantGroup) => {
    setStatusMessage(null);
    setSelected(prev => {
      const next = { ...prev };
      for (const variant of group.variants) {
        delete next[variant.name];
      }
      return next;
    });
  };

  const exportPayload = useMemo(
    () => ({
      include: selectedVariants.map(v => v.name),
      remove: removedCanonicals.map(v => v.name),
    }),
    [selectedVariants, removedCanonicals]
  );

  const exportPreview = useMemo(
    () => JSON.stringify(exportPayload, null, 2),
    [exportPayload]
  );

  const handleCopy = async () => {
    try {
      const payload = JSON.stringify(exportPayload, null, 2);
      await navigator.clipboard.writeText(payload);
      setStatusMessage('Copied selection to clipboard.');
    } catch (error) {
      console.error('Failed to copy selection', error);
      setStatusMessage('Could not copy to clipboard. Copy manually from below.');
    }
  };

  const handleDownload = () => {
    const payload = JSON.stringify(exportPayload, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'selected-variant-punks.json';
    anchor.click();
    URL.revokeObjectURL(url);
    setStatusMessage('Saved selection as file.');
  };

  const hasSelections = selectedVariants.length > 0 || removedCanonicals.length > 0;

  if (groups.length === 0) {
    return (
      <div className="mt-12 text-center text-[#c9a96e]/70">
        No variant files detected. Everything already matches the validated list.
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <section className="bg-[#1c1814] border border-[#c9a96e]/20 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="serif text-xl text-[#c9a96e] tracking-wider">
              Selection Summary
            </h2>
            <p className="text-xs text-[#c9a96e]/60 uppercase tracking-[0.3em]">
              {selectedVariants.length} VARIANTS MARKED FOR INCLUSION ·{' '}
              {removedCanonicals.length} CANONICALS MARKED FOR REMOVAL
            </p>
            <p className="mt-3 text-[11px] leading-relaxed text-[#c9a96e]/55 max-w-xl">
              Every group shows the{' '}
              <span className="text-[#c9a96e] font-medium">
                current collection image
              </span>{' '}
              on the left. Use the button below it to flag that canonical for
              removal. Cards on the right are{' '}
              <span className="text-[#c9a96e] font-medium">
                not in the collection yet
              </span>
              ; toggle them to mark which alternates you want to include.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleCopy}
              className="px-4 py-2 text-xs tracking-widest border border-[#c9a96e]/40 text-[#c9a96e]/70 hover:text-[#0a0806] hover:bg-[#c9a96e] transition"
            >
              COPY LIST
            </button>
            <button
              onClick={handleDownload}
              className="px-4 py-2 text-xs tracking-widest border border-[#c9a96e]/40 text-[#c9a96e]/70 hover:text-[#0a0806] hover:bg-[#c9a96e] transition"
            >
              DOWNLOAD JSON
            </button>
            {hasSelections && (
              <button
                onClick={() => {
                  setSelected({});
                  setRemovedCanon({});
                  setStatusMessage('Cleared all selections.');
                }}
                className="px-4 py-2 text-xs tracking-widest border border-[#c9a96e]/20 text-[#c9a96e]/50 hover:text-[#0a0806] hover:bg-[#c9a96e]/70 transition"
              >
                CLEAR ALL
              </button>
            )}
          </div>
        </div>
        {statusMessage && (
          <p className="mt-4 text-xs text-[#c9a96e]/50 tracking-widest">
            {statusMessage}
          </p>
        )}
        <div className="mt-4 bg-black/40 border border-[#c9a96e]/10 p-4 overflow-auto max-h-60">
          <pre className="text-xs text-[#c9a96e]/80 whitespace-pre-wrap">
            {hasSelections ? exportPreview : '// Select variants or flag canonicals to build the list'}
          </pre>
        </div>
      </section>

      {groups.map(group => (
        <section
          key={group.baseId}
          className="border border-[#c9a96e]/20 bg-[#14110e]/80"
        >
          <div className="flex flex-col gap-4 border-b border-[#c9a96e]/10 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="serif text-lg text-[#c9a96e] tracking-wider">
                {group.baseId.toUpperCase()}
              </h3>
              <p className="text-xs text-[#c9a96e]/50 tracking-[0.3em]">
                {group.variants.length} VARIANT{group.variants.length > 1 ? 'S' : ''}
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => handleSelectAll(group)}
                className="px-4 py-2 text-[10px] tracking-widest border border-[#c9a96e]/30 text-[#c9a96e]/70 hover:text-[#0a0806] hover:bg-[#c9a96e] transition"
              >
                SELECT ALL
              </button>
              <button
                onClick={() => handleClearGroup(group)}
                className="px-4 py-2 text-[10px] tracking-widest border border-[#c9a96e]/30 text-[#c9a96e]/70 hover:text-[#0a0806] hover:bg-[#c9a96e] transition"
              >
                CLEAR GROUP
              </button>
            </div>
          </div>

          <div className="grid gap-6 p-6 md:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
            <div className="border border-[#c9a96e]/20 relative">
              {group.canonical && (
                <span
                  className={`absolute left-3 top-3 px-2 py-1 text-[9px] tracking-[0.25em] ${
                    removedCanon[group.canonical.name]
                      ? 'bg-red-500 text-white'
                      : 'bg-[#c9a96e] text-[#0a0806]'
                  }`}
                >
                  {removedCanon[group.canonical.name]
                    ? 'MARKED TO REMOVE'
                    : 'INCLUDED'}
                </span>
              )}
              <div className="bg-[#0a0806] aspect-square flex items-center justify-center">
                {group.canonical ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={group.canonical.src}
                    alt={group.canonical.name}
                    className="w-full h-full object-contain"
                    style={{ imageRendering: 'pixelated' }}
                  />
                ) : (
                  <div className="text-xs text-[#c9a96e]/50 tracking-widest text-center px-6">
                    No canonical image found for this base ID
                  </div>
                )}
              </div>
              <div className="border-t border-[#c9a96e]/10 p-4">
                <p className="text-[11px] text-[#c9a96e] tracking-widest">CANONICAL</p>
                <p className="text-xs text-[#c9a96e]/60 break-all mt-1">
                  {group.canonical ? group.canonical.name : 'Not defined'}
                </p>
                {group.canonical && (
                  <button
                    onClick={() => toggleCanonical(group.canonical!.name)}
                    className={`mt-4 w-full px-3 py-2 text-[10px] tracking-widest border transition ${
                      removedCanon[group.canonical.name]
                        ? 'border-red-400 bg-red-500 text-white hover:border-red-300 hover:bg-red-400'
                        : 'border-[#c9a96e]/40 text-[#c9a96e]/80 hover:border-[#c9a96e] hover:text-[#0a0806] hover:bg-[#c9a96e]'
                    }`}
                  >
                    {removedCanon[group.canonical.name]
                      ? 'UNDO REMOVE'
                      : 'REMOVE FROM COLLECTION'}
                  </button>
                )}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {group.variants.map(variant => {
                const isSelected = Boolean(selected[variant.name]);
                const statusLabel = isSelected ? 'MARKED FOR INCLUSION' : 'NOT IN COLLECTION';
                return (
                  <div
                    key={variant.name}
                    className={`border transition ${
                      isSelected
                        ? 'border-[#c9a96e] bg-[#c9a96e]/10 shadow-[0_0_0_1px_rgba(201,169,110,0.5)]'
                        : 'border-[#c9a96e]/20 bg-black/40'
                    }`}
                  >
                    <div className="relative bg-[#0a0806] aspect-square flex items-center justify-center">
                      <span
                        className={`absolute left-2 top-2 px-2 py-1 text-[9px] tracking-[0.25em] ${
                          isSelected
                            ? 'bg-[#c9a96e] text-[#0a0806]'
                            : 'bg-black/70 text-[#c9a96e]/70'
                        }`}
                      >
                        {statusLabel}
                      </span>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={variant.src}
                        alt={variant.name}
                        className="w-full h-full object-contain"
                        style={{ imageRendering: 'pixelated' }}
                      />
                    </div>
                    <div className="border-t border-[#c9a96e]/10 p-4 space-y-3">
                      <p className="text-xs text-[#c9a96e]/70 break-all">
                        {variant.name}
                      </p>
                      <button
                        onClick={() => toggleVariant(variant.name)}
                        className={`w-full px-3 py-2 text-[10px] tracking-widest border transition ${
                          isSelected
                            ? 'border-[#c9a96e] bg-[#c9a96e] text-[#0a0806]'
                            : 'border-[#c9a96e]/40 text-[#c9a96e]/80 hover:border-[#c9a96e] hover:text-[#0a0806] hover:bg-[#c9a96e]'
                        }`}
                      >
                        {isSelected ? 'SELECTED' : 'SELECT TO INCLUDE'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ))}
    </div>
  );
}

