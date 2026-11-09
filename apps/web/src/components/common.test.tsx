import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import axe from 'axe-core'
import { EmptyState, ErrorState, Badge, Modal, PageHeader, ConfirmDialog } from './common'

async function expectNoCriticalViolations(container: HTMLElement) {
  const { violations } = await axe.run(container, { runOnly: ['wcag2a', 'wcag2aa'] })
  const critical = violations.filter((v) => v.impact === 'critical' || v.impact === 'serious')
  expect(critical.map((v) => `${v.id}: ${v.help}`)).toEqual([])
}

describe('common components', () => {
  it('renders EmptyState', () => {
    render(<EmptyState title="No sources yet" hint="Add your first source on the left." />)
    expect(screen.getByText('No sources yet')).toBeInTheDocument()
    expect(screen.getByText('Add your first source on the left.')).toBeInTheDocument()
  })

  it('renders ErrorState with retry', () => {
    const onRetry = vi.fn()
    render(<ErrorState message="boom" onRetry={onRetry} />)
    expect(screen.getByText('boom')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /retry/i }))
    expect(onRetry).toHaveBeenCalled()
  })

  it('renders Badge with tone class', () => {
    const { container } = render(<Badge tone="warn">soon</Badge>)
    expect(screen.getByText('soon')).toBeInTheDocument()
    expect(container.querySelector('.sb-badge-warn')).not.toBeNull()
  })

  it('renders PageHeader with h1', () => {
    render(<PageHeader title="Dashboard" sub="Overview" />)
    const h1 = screen.getByRole('heading', { level: 1 })
    expect(h1).toHaveTextContent('Dashboard')
  })

  it('Modal focuses itself, closes on Escape and backdrop', () => {
    const onClose = vi.fn()
    const { container } = render(
      <Modal title="Confirm" onClose={onClose}>
        <p>body</p>
      </Modal>,
    )
    const dialog = screen.getByRole('dialog', { name: /confirm/i })
    expect(dialog).toBeInTheDocument()
    expect(document.activeElement).toBe(container.querySelector('.sb-modal'))
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
    fireEvent.click(container.querySelector('.sb-modal-backdrop') as Element)
    expect(onClose).toHaveBeenCalledTimes(2)
  })

  it('ConfirmDialog renders both actions', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()
    render(<ConfirmDialog title="Delete?" body="Sure?" onConfirm={onConfirm} onCancel={onCancel} />)
    fireEvent.click(screen.getByRole('button', { name: /^confirm$/i }))
    expect(onConfirm).toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: /^cancel$/i }))
    expect(onCancel).toHaveBeenCalled()
  })

  it('axe: EmptyState has zero critical/serious violations', async () => {
    const { container } = render(<EmptyState title="No sources yet" hint="Add one." />)
    await expectNoCriticalViolations(container)
  })

  it('axe: ErrorState has zero critical/serious violations', async () => {
    const { container } = render(<ErrorState message="boom" onRetry={() => {}} />)
    await expectNoCriticalViolations(container)
  })

  it('axe: Modal has zero critical/serious violations', async () => {
    const { container } = render(
      <Modal title="Confirm" onClose={() => {}}>
        <p>body</p>
        <button>OK</button>
      </Modal>,
    )
    await expectNoCriticalViolations(container)
  })

  it('axe: PageHeader + Badge shell has zero critical/serious violations', async () => {
    const { container } = render(
      <div>
        <PageHeader title="Dashboard" sub="Overview" />
        <Badge tone="ok">ok</Badge>
      </div>,
    )
    await expectNoCriticalViolations(container)
  })
})
