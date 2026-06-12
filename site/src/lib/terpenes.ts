// Content map for terpene hub pages. Keys must match terpene_name values
// in the Supabase `terpenes` table (lowercase, single word).

export type TerpeneFaq = { question: string; answer: string }

export type TerpeneEntry = {
  slug: string
  displayName: string
  shortDescription: string
  seoTitle: string
  seoDescription: string
  faqs: [TerpeneFaq, TerpeneFaq, TerpeneFaq]
}

export const TERPENES: Record<string, TerpeneEntry> = {
  myrcene: {
    slug: 'myrcene',
    displayName: 'Myrcene',
    shortDescription:
      'Myrcene is the most common terpene in cannabis, responsible for the earthy, musky, herbal aroma of many indica-leaning strains. ' +
      'It is widely associated with sedating, body-heavy effects, and is also found in mango, hops, and lemongrass. ' +
      'Cannabis with myrcene above roughly 0.5% is often described as having a "couch-lock" character.',
    seoTitle: 'Myrcene Terpene — Effects, Aroma & Cannabis Strains | The Strain Report',
    seoDescription:
      'Myrcene is the most common cannabis terpene. Learn its earthy aroma, sedating effects, and browse the strains highest in myrcene.',
    faqs: [
      {
        question: 'What does myrcene smell like?',
        answer:
          'Earthy, musky, and herbal with hints of clove and ripe fruit. It is the dominant aroma compound in many "skunky" cannabis strains and is also responsible for the smell of mango and hops.',
      },
      {
        question: 'Is myrcene responsible for indica effects?',
        answer:
          'Strains high in myrcene (typically above 0.5%) are commonly associated with the sedating, body-heavy effects labeled "indica," and myrcene is often cited as a contributor. The exact mechanism is still under active research.',
      },
      {
        question: 'What other plants contain myrcene?',
        answer:
          'Mango, hops, lemongrass, thyme, and bay leaves. Mango is the most widely cited dietary source — anecdotally, eating mango before consuming cannabis is said to amplify effects, though clinical evidence remains thin.',
      },
    ],
  },

  caryophyllene: {
    slug: 'caryophyllene',
    displayName: 'Caryophyllene',
    shortDescription:
      'Beta-caryophyllene is a peppery, spicy terpene found in black pepper, cloves, and cinnamon. ' +
      'It is the only common cannabis terpene that binds directly to the body\'s CB2 cannabinoid receptors, ' +
      'giving it cannabinoid-like behavior and notable anti-inflammatory and analgesic effects in research.',
    seoTitle: 'Caryophyllene Terpene — The CB2-Binding Terpene | The Strain Report',
    seoDescription:
      'Caryophyllene is the peppery, spicy cannabis terpene that uniquely binds CB2 receptors. Learn its effects and the strains highest in caryophyllene.',
    faqs: [
      {
        question: 'What makes caryophyllene unique among terpenes?',
        answer:
          'It is the only common terpene known to bind directly to the body\'s CB2 cannabinoid receptors, behaving more like a cannabinoid than a typical terpene. This dual identity is why it gets so much attention in pharmacological research.',
      },
      {
        question: 'What does caryophyllene smell like?',
        answer:
          'Peppery, spicy, and woody — the same dominant aroma compound you find in black pepper, cloves, and cinnamon.',
      },
      {
        question: 'Is caryophyllene anti-inflammatory?',
        answer:
          'Animal and in vitro studies suggest caryophyllene has anti-inflammatory and analgesic effects via CB2 binding. Clinical human evidence is still limited but growing.',
      },
    ],
  },

  limonene: {
    slug: 'limonene',
    displayName: 'Limonene',
    shortDescription:
      'Limonene is a bright, citrus-forward terpene most associated with lemon, orange, and other citrus rinds. ' +
      'In cannabis it is often linked to mood-elevating, anxiolytic effects, and it is the second most common terpene after myrcene. ' +
      'It also shows up across the food and cosmetics industries as a natural citrus flavoring.',
    seoTitle: 'Limonene Terpene — Citrus, Mood & Cannabis Strains | The Strain Report',
    seoDescription:
      'Limonene is the bright, citrus cannabis terpene. Learn its mood-elevating effects and explore the strains richest in limonene.',
    faqs: [
      {
        question: 'What does limonene smell like?',
        answer:
          'Bright citrus — lemon, orange, and grapefruit notes. It is the dominant aroma compound in citrus rinds, which is why citrus-forward strains often test high for limonene.',
      },
      {
        question: 'Does limonene help with anxiety?',
        answer:
          'Several animal studies suggest limonene has anxiolytic and mood-elevating effects. Human data is mostly drawn from aromatherapy and small clinical trials, so results should be treated as suggestive rather than definitive.',
      },
      {
        question: 'What other plants contain limonene?',
        answer:
          'Lemon, orange, lime, and grapefruit are the most prominent sources, plus juniper, rosemary, and peppermint. Citrus peel oil is roughly 90% limonene by weight.',
      },
    ],
  },

  linalool: {
    slug: 'linalool',
    displayName: 'Linalool',
    shortDescription:
      'Linalool is a floral, lavender-like terpene best known as the active compound in lavender essential oil. ' +
      'In cannabis it is associated with calming, sedating, and anxiolytic effects, and it shows up prominently in strains used for relaxation and sleep. ' +
      'It is also widely studied for its role in aromatherapy.',
    seoTitle: 'Linalool Terpene — Lavender, Calm & Cannabis Strains | The Strain Report',
    seoDescription:
      'Linalool is the calming, lavender-aroma cannabis terpene. Learn its sedating effects and find the strains highest in linalool.',
    faqs: [
      {
        question: 'What does linalool smell like?',
        answer:
          'Floral and lavender-like with subtle spice — the same aroma compound that makes lavender essential oil distinctive.',
      },
      {
        question: 'Can linalool help with sleep?',
        answer:
          'Linalool is well-studied as a calming, anxiolytic compound. Inhaled lavender (which is high in linalool) has shown some benefit for sleep quality in clinical research, though most cannabis-specific studies remain preclinical.',
      },
      {
        question: 'What other plants contain linalool?',
        answer:
          'Lavender is the most cited source, but linalool is also found in rosewood, mint, basil, and certain citrus species. It is one of the most common floral aroma compounds in nature.',
      },
    ],
  },

  pinene: {
    slug: 'pinene',
    displayName: 'Pinene',
    shortDescription:
      'Pinene is a fresh, conifer-like terpene that smells exactly as the name suggests — pine forest, rosemary, and basil. ' +
      'It is one of the most abundant terpenes in nature and is being studied as a bronchodilator and a possible counter to THC\'s short-term memory effects. ' +
      'Cannabis chemovars high in pinene often share a clear, focused profile.',
    seoTitle: 'Pinene Terpene — Pine Aroma & Focused Effects | The Strain Report',
    seoDescription:
      'Pinene is the pine-scented cannabis terpene linked to alertness and bronchodilation. Learn its effects and the strains highest in pinene.',
    faqs: [
      {
        question: 'What does pinene smell like?',
        answer:
          'Fresh pine, conifer forest, and rosemary — exactly what the name suggests. It is the dominant aroma in pine needles.',
      },
      {
        question: 'Does pinene affect memory?',
        answer:
          'Some research suggests alpha-pinene may counteract the short-term memory impairment associated with THC, possibly through acetylcholinesterase inhibition. Findings are preliminary and largely preclinical.',
      },
      {
        question: 'What is the difference between alpha-pinene and beta-pinene?',
        answer:
          'Both are isomers commonly found in cannabis. Alpha-pinene has a sharper, drier pine scent and is more abundant; beta-pinene has a softer, herbal edge closer to dill or basil.',
      },
    ],
  },

  terpinolene: {
    slug: 'terpinolene',
    displayName: 'Terpinolene',
    shortDescription:
      'Terpinolene has a complex aroma — fresh, herbal, slightly floral, with hints of citrus and pine. ' +
      'It is less common as a dominant terpene, but when it is dominant, it tends to appear in sativa-leaning chemovars like Jack Herer and Dutch Treat. ' +
      'It also occurs in nutmeg, tea tree, and lilacs.',
    seoTitle: 'Terpinolene Terpene — Sativa Aroma & Cannabis Strains | The Strain Report',
    seoDescription:
      'Terpinolene is the complex, herbal cannabis terpene linked to uplifting sativa profiles. Learn its character and find the strains highest in terpinolene.',
    faqs: [
      {
        question: 'What does terpinolene smell like?',
        answer:
          'Complex and changeable — fresh, herbal, with hints of citrus, pine, and floral notes. It is often described as the "uplifting" aroma in sativa-leaning strains.',
      },
      {
        question: 'Is terpinolene common in cannabis?',
        answer:
          'It is less common as a dominant terpene than myrcene or caryophyllene. When it is dominant, it typically shows up in sativa-leaning chemovars like Jack Herer, Dutch Treat, and several haze descendants.',
      },
      {
        question: 'What other plants contain terpinolene?',
        answer:
          'Nutmeg, tea tree, lilacs, apples, and several conifer species. It is also widely used in soaps and perfumes for its fresh, slightly sweet aroma.',
      },
    ],
  },
}

export const TERPENE_SLUGS = Object.keys(TERPENES)

// Database stores terpene_name in title case (e.g. "Myrcene"), but our URL
// slugs are lowercase. These display-name values are what to send to Supabase.
export const TERPENE_DISPLAY_NAMES = Object.values(TERPENES).map((t) => t.displayName)

// Map a stored DB value back to its slug — for grouping query results.
export const TERPENE_DISPLAY_TO_SLUG: Record<string, string> = Object.fromEntries(
  Object.values(TERPENES).map((t) => [t.displayName, t.slug]),
)

export function getTerpene(slug: string): TerpeneEntry | null {
  return TERPENES[slug] ?? null
}

export function hasTerpeneHub(name: string): boolean {
  return name.toLowerCase() in TERPENES
}
