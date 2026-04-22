export default function PrivacyModal({ onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="card max-w-lg w-full max-h-[80vh] overflow-y-auto space-y-4">
        <div className="flex justify-between items-start">
          <h2 className="text-lg font-bold text-lol-gold">Privacy Policy</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl leading-none ml-4"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <p className="text-xs text-gray-500">Last updated: April 22, 2026</p>

        <div className="text-sm text-gray-300 space-y-4">
          <section>
            <h3 className="font-semibold text-white mb-1">What we collect</h3>
            <p>
              CleverPachonc collects only the Riot ID (summoner name and tag) and region
              you enter into the search field. This information is used exclusively to query
              the Riot Games API on your behalf and is never stored, logged, or shared.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-white mb-1">What we do not store</h3>
            <p>
              This application has no database. All summoner statistics are fetched
              in real-time from the Riot Games API and exist only in your browser for
              the duration of your session. We do not retain, sell, or share any
              personal data.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-white mb-1">Third-party services</h3>
            <p>
              This application uses the Riot Games API to retrieve publicly available
              summoner statistics. By using CleverPachonc you agree to be bound by the{' '}
              <a
                href="https://www.riotgames.com/en/terms-of-service"
                target="_blank"
                rel="noopener noreferrer"
                className="text-lol-gold hover:underline"
              >
                Riot Games Terms of Service
              </a>
              . Champion icons and game assets are served directly from the Data Dragon CDN
              operated by Riot Games.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-white mb-1">Cookies and analytics</h3>
            <p>
              CleverPachonc does not use cookies, tracking pixels, or any analytics service.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-white mb-1">Contact</h3>
            <p>
              For questions about this privacy policy, open an issue on the project&apos;s
              GitHub repository.
            </p>
          </section>
        </div>

        <button
          onClick={onClose}
          className="w-full mt-2 py-2 rounded text-sm bg-lol-card border border-lol-border
                     text-gray-400 hover:text-white hover:border-lol-gold transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  )
}
