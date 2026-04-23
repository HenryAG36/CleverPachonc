import { useState } from 'react'
import PrivacyModal from './PrivacyModal'

export default function Footer() {
  const [showPrivacy, setShowPrivacy] = useState(false)

  return (
    <footer className="mt-16 border-t border-apple-separator">
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-3">
        <p className="text-xs text-apple-text-tertiary text-center leading-relaxed">
          CleverPachonc isn&apos;t endorsed by Riot Games and doesn&apos;t reflect the views or
          opinions of Riot Games or anyone officially involved in producing or managing Riot Games
          properties. Riot Games, League of Legends and all associated properties are trademarks
          or registered trademarks of Riot Games, Inc.
        </p>
        <div className="flex justify-center gap-6 text-xs">
          <button
            onClick={() => setShowPrivacy(true)}
            className="text-apple-text-tertiary hover:text-apple-text-secondary transition-colors"
          >
            Privacy Policy
          </button>
          <a
            href="https://developer.riotgames.com/policies/general"
            target="_blank"
            rel="noopener noreferrer"
            className="text-apple-text-tertiary hover:text-apple-text-secondary transition-colors"
          >
            Riot API Policy
          </a>
        </div>
      </div>
      {showPrivacy && <PrivacyModal onClose={() => setShowPrivacy(false)} />}
    </footer>
  )
}
