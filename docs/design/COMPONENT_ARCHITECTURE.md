# Component Architecture
`src/components/common.tsx`: Layout, PageHeader, StatCard, Badge, EmptyState, ErrorState, LoadingSkeleton, Modal, ConfirmDialog. Pages own their data fetching via a small `useFetch` hook in `src/App.tsx`; API functions live in `src/api/client.ts`.
