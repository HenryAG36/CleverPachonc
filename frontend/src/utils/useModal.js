import { useEffect, useRef } from 'react'

// Shared modal behavior: Escape-to-close (topmost modal only), body scroll
// lock that survives stacked modals closing in any order, focus moved into
// the dialog on open and restored on close, and a Tab focus trap.
const modalStack = []

function updateBodyLock() {
  document.body.style.overflow = modalStack.length > 0 ? 'hidden' : ''
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function useModal(onClose) {
  const containerRef = useRef(null)
  const onCloseRef = useRef(onClose)
  onCloseRef.current = onClose

  useEffect(() => {
    const id = {}
    modalStack.push(id)
    updateBodyLock()
    const previouslyFocused = document.activeElement
    const container = containerRef.current
    container?.focus()

    function handleKeydown(e) {
      if (modalStack[modalStack.length - 1] !== id) return // only the topmost modal reacts
      if (e.key === 'Escape') {
        onCloseRef.current()
        return
      }
      if (e.key === 'Tab' && container) {
        const focusable = [...container.querySelectorAll(FOCUSABLE)]
        if (!focusable.length) {
          e.preventDefault()
          return
        }
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (!container.contains(document.activeElement)) {
          e.preventDefault()
          first.focus()
        } else if (e.shiftKey && (document.activeElement === first || document.activeElement === container)) {
          e.preventDefault()
          last.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }

    window.addEventListener('keydown', handleKeydown)
    return () => {
      window.removeEventListener('keydown', handleKeydown)
      const idx = modalStack.indexOf(id)
      if (idx !== -1) modalStack.splice(idx, 1)
      updateBodyLock()
      previouslyFocused?.focus?.()
    }
  }, [])

  return containerRef
}
