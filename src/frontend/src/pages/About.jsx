const REFERENCES = [
  {
    citation:
      'Hughes, T.P., Kerry, J.T., Álvarez-Noriega, M., et al. (2017). Global warming and recurrent mass bleaching of corals. Nature, 543, 373–377.',
  },
  {
    citation:
      'Hughes, T.P., Anderson, K.D., Connolly, S.R., et al. (2018). Spatial and temporal patterns of mass bleaching of corals in the Anthropocene. Science, 359(6371), 80–83.',
  },
  {
    citation:
      "Hoegh-Guldberg, O. (1999). Climate change, coral bleaching and the future of the world's coral reefs. Marine and Freshwater Research, 50(8), 839–866.",
  },
  {
    citation: 'NOAA Coral Reef Watch — satellite-based coral bleaching heat stress monitoring.',
    url: 'https://coralreefwatch.noaa.gov/',
    label: 'coralreefwatch.noaa.gov',
  },
  {
    citation:
      'Siebeck, U.E., Marshall, N.J., Kluter, A., & Hoegh-Guldberg, O. (2006). Monitoring coral bleaching using a colour reference card. Coral Reefs, 25(3), 453–460.',
  },
  {
    citation:
      'AI Alliance (Team 319). (2026). Assessment of Coral Reef Health: Equipment, Survey Methods and Practical Criteria for Distinguishing Dead Coral in the Context of the Fourth Global Bleaching Event.',
    url: 'https://github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance/blob/main/docs/reef-survey-methodology.md',
    label: 'Read the team’s field methodology paper',
  },
]

const ALERT_LEVELS = [
  { level: 'Watch', threshold: 'SST > Monthly Mean Max', meaning: 'Bleaching possible on the most sensitive reefs' },
  { level: 'Warning', threshold: 'HotSpot > 0 °C', meaning: 'Heat stress accumulating' },
  { level: 'Alert Level 1', threshold: 'DHW ≥ 4 °C-weeks', meaning: 'Significant bleaching likely' },
  { level: 'Alert Level 2', threshold: 'DHW ≥ 8 °C-weeks', meaning: 'Bleaching + some mortality likely' },
  { level: 'Alert Level 3', threshold: 'DHW ≥ 12 °C-weeks', meaning: 'Mortality likely across many species' },
  { level: 'Alert Level 4', threshold: 'DHW ≥ 16 °C-weeks', meaning: 'Widespread mortality risk' },
  { level: 'Alert Level 5', threshold: 'DHW ≥ 20 °C-weeks', meaning: 'Near-total mortality risk' },
]

function scholarSearchUrl(citation) {
  return `https://scholar.google.com/scholar?q=${encodeURIComponent(citation)}`
}

export default function About() {
  return (
    <div className="mx-auto max-w-3xl space-y-12 pb-16">
      <section className="text-center">
        <h1 className="text-3xl font-bold text-ocean-900">The Science Behind CoralAI</h1>
        <p className="mt-3 text-slate-600">
          Why coral bleaching matters, what causes it, and how this tool turns a photo into a
          health assessment.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-ocean-900">What is coral bleaching?</h2>
        <p className="text-slate-600">
          Coral gets its color — and most of its food — from microscopic algae (zooxanthellae)
          living in its tissue. When water gets too warm, that partnership breaks down: the coral
          expels the algae and turns ghostly white. A bleached coral isn&apos;t dead yet, but
          it&apos;s starving and far more vulnerable to disease. If warm water persists for weeks, bleached
          coral dies.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-ocean-900">Why it&apos;s accelerating</h2>
        <p className="text-slate-600">
          Mass bleaching events — where entire reef systems bleach at once — used to be rare.
          Hughes et al. (2017, 2018) documented that recurrent mass bleaching driven by marine
          heatwaves is now hitting reefs too frequently for them to recover between events. Reefs
          support roughly a quarter of all marine species and protect coastlines for hundreds of
          millions of people, which is why tracking bleaching at scale — not just at the handful
          of reefs research teams can visit in person — matters.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-ocean-900">How CoralAI&apos;s classification works</h2>
        <p className="text-slate-600">
          Every uploaded photo is sent to Google&apos;s Gemini Vision model with a strict prompt that
          forces a structured response: a classification (Healthy, Partially Bleached, Severely
          Bleached, Dead Coral, or Unknown), a confidence score, and a plain-language recommendation.
          That result is combined with real-time sea temperature from Open-Meteo and NASA into a
          simple, explainable Coral Risk Score — no black box, just a classification plus a
          temperature threshold check.
        </p>
        <p className="text-slate-600">
          This is a screening tool, not a replacement for a marine biologist. Low-confidence or
          borderline results should be verified in person before being used in formal reporting —
          the same disclaimer appears on every generated PDF report.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-ocean-900">Grounded in field survey standards</h2>
        <p className="text-slate-600">
          CoralAI&apos;s risk engine isn&apos;t a black box tuned by eye — it implements the same NOAA
          Coral Reef Watch Bleaching Alert Level thresholds documented in our team&apos;s reef survey
          methodology paper, extended to Alert Level 5 after the record-breaking Fourth Global Coral
          Bleaching Event (2023–2025). Every survey&apos;s coordinates are checked live against NOAA&apos;s
          satellite Degree Heating Week (DHW) data and classified using this exact table:
        </p>
        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-100 text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-2">Level</th>
                <th className="px-4 py-2">Threshold</th>
                <th className="px-4 py-2">Meaning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {ALERT_LEVELS.map((row) => (
                <tr key={row.level}>
                  <td className="px-4 py-2 font-medium text-slate-700">{row.level}</td>
                  <td className="px-4 py-2 text-slate-500">{row.threshold}</td>
                  <td className="px-4 py-2 text-slate-500">{row.meaning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-slate-600">
          One honest limitation: the paper&apos;s Coral Mortality Index (CMI) is a site-level metric —
          it needs live/dead percent cover measured across a full Line Intercept Transect or set of
          quadrats, which a single photo can&apos;t produce. CoralAI classifies individual photos as a
          fast screening signal, not a replacement for the full transect protocol described in the
          paper when a formal CMI is required.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-ocean-900">References &amp; further reading</h2>
        <ul className="space-y-3">
          {REFERENCES.map((ref) => (
            <li key={ref.citation} className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
              <p className="text-slate-700">{ref.citation}</p>
              <a
                href={ref.url ?? scholarSearchUrl(ref.citation)}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 inline-block text-ocean-700 hover:underline"
              >
                {ref.label ?? 'Find this paper on Google Scholar →'}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
