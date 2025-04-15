export function BackgroundGradient() {
  return (
    <div className="fixed inset-0 -z-10">
      <div className="absolute inset-0 bg-gradient-to-br from-skyblue-light via-white/80 to-purple-light" />
      <div className="absolute inset-0 opacity-10 bg-[url('/images/grid-pattern.png')] bg-repeat"></div>
    </div>
  )
}
