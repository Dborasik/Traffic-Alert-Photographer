interface Props {
  src: string | null
  onClose: () => void
}

export default function Lightbox({ src, onClose }: Props) {
  return (
    <div className={`lightbox${src ? ' open' : ''}`} onClick={onClose}>
      {src && <img src={src} alt="" />}
    </div>
  )
}
