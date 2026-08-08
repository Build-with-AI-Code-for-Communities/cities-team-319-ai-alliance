export default function Loader({ label = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-ocean-200 border-t-ocean-600" />
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  )
}
