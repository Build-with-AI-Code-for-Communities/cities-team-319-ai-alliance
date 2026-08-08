import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'

// Work around Leaflet's default marker icons not resolving under Vite's bundler.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export default function MapView({ latitude, longitude, label = 'Survey location' }) {
  if (latitude == null || longitude == null) {
    return (
      <div className="flex h-full w-full items-center justify-center rounded-xl bg-slate-100 text-sm text-slate-400">
        No GPS location available for this survey
      </div>
    )
  }

  const position = [latitude, longitude]

  return (
    <MapContainer center={position} zoom={12} className="h-full w-full" scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={position}>
        <Popup>{label}</Popup>
      </Marker>
    </MapContainer>
  )
}
