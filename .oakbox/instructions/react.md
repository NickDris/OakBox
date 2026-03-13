# React & TypeScript Conventions & Style Guide

## Runtime & Package Management

- **Node version:** 20 LTS (enforced via `.nvmrc`)
- **Package manager:** npm (use `package-lock.json`, always commit it)
- **Bundler:** Vite

### Common commands

```bash
npm install              # Install all dependencies from lockfile
npm install <package>    # Add a production dependency
npm install -D <package> # Add a development dependency
npm uninstall <package>  # Remove a dependency
npm run dev              # Start dev server
npm run build            # Production build
npm run lint             # Run ESLint
npm run typecheck        # Run tsc --noEmit
npm run test             # Run Vitest
```

> Never use `yarn` or `pnpm`. All dependency changes go through `npm`.

---

## Project Layout

```
src/
  frontend/
    index.html
    main.tsx                    # App entry point
    App.tsx                     # Root component
    components/                 # Shared/reusable UI components
      Button/
        Button.tsx
        Button.test.tsx
        index.ts                # Re-export
    features/                   # Feature-based modules
      auth/
        components/
        hooks/
        api.ts
        types.ts
        index.ts
    hooks/                      # Shared custom hooks
    lib/                        # Utility functions & API client
      api-client.ts
    types/                      # Shared TypeScript types
      index.ts
    styles/                     # Global styles, theme tokens
    routes/                     # Route definitions
    vite.config.ts
    tsconfig.json
    package.json
    package-lock.json
    .nvmrc
tests/
  frontend/
    setup.ts                    # Vitest global setup
```

---

## TypeScript Configuration

```jsonc
// tsconfig.json — non-negotiable settings
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/frontend/*"]
    }
  }
}
```

- `strict: true` is mandatory — never disable it.
- Never use `any`. Use `unknown` and narrow with type guards.
- Never use `@ts-ignore`. Use `@ts-expect-error` with a comment only as a last resort.
- Never use non-null assertion (`!`) unless you add a comment explaining why it is safe.

---

## Code Style

### Formatting & Linting

- **Formatter:** Prettier (printWidth 80, singleQuote true, trailingComma all)
- **Linter:** ESLint with `@typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-jsx-a11y`

```json
// .prettierrc
{
  "printWidth": 80,
  "singleQuote": true,
  "trailingComma": "all",
  "semi": true,
  "tabWidth": 2
}
```

### Naming Conventions

| Construct          | Convention          | Example                     |
|--------------------|---------------------|-----------------------------|
| Component          | `PascalCase`        | `UserProfile.tsx`           |
| Hook               | `camelCase`         | `useAuth.ts`                |
| Utility function   | `camelCase`         | `formatCurrency()`          |
| Constant           | `UPPER_SNAKE_CASE`  | `MAX_PAGE_SIZE`             |
| Type / Interface   | `PascalCase`        | `UserProfile`               |
| Enum               | `PascalCase`        | `UserRole.Admin`            |
| Props type         | `PascalCase`        | `UserCardProps`             |
| CSS class (module) | `camelCase`         | `styles.cardHeader`         |
| File (component)   | `PascalCase`        | `UserCard.tsx`              |
| File (utility)     | `camelCase`         | `formatDate.ts`             |
| Directory          | `kebab-case`        | `user-profile/`             |

### Component Conventions

- **Functional components only.** No class components.
- **Named exports only.** No default exports.

```tsx
// Good
export function UserCard({ name, email }: UserCardProps) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{email}</p>
    </div>
  );
}

// Bad — default export
export default function UserCard() { ... }
```

- Collocate component, test, and styles in the same directory.
- One component per file.
- Props interface defined in the same file, directly above the component.

### Type Definitions

- Prefer `interface` for object shapes that may be extended.
- Prefer `type` for unions, intersections, and mapped types.
- Suffix props types with `Props`: `UserCardProps`.
- Never prefix interfaces with `I` (no `IUser`).

```tsx
interface UserCardProps {
  name: string;
  email: string;
  role: UserRole;
  onEdit?: (id: string) => void;
}
```

### Hooks

- Custom hooks must start with `use`.
- Extract logic into custom hooks when a component exceeds ~50 lines of non-JSX code.
- Never call hooks conditionally.

```tsx
export function useUser(id: string) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchUser(id).then((data) => {
      if (!cancelled) {
        setUser(data);
        setIsLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [id]);

  return { user, isLoading };
}
```

### State Management

- **Local state:** `useState` / `useReducer`.
- **Server state:** React Query (`@tanstack/react-query`).
- **Global client state:** React Context (small scope) or Zustand (larger scope).
- Never put server-fetched data in global state — use React Query's cache.

### Event Handlers

- Prefix with `handle`: `handleClick`, `handleSubmit`.
- Props callbacks prefix with `on`: `onClick`, `onSubmit`.

---

## Imports

- Sort order (enforced by ESLint): react → third-party → `@/` aliases → relative.
- Use path aliases (`@/components/...`) for cross-feature imports.
- Use relative imports within the same feature directory.

```tsx
import { useState } from 'react';

import { useQuery } from '@tanstack/react-query';

import { Button } from '@/components/Button';
import { UserCard } from './components/UserCard';
```

---

## Testing

- **Framework:** Vitest + React Testing Library
- **Runner:** `npm run test`
- **File naming:** `<Component>.test.tsx` or `<util>.test.ts`, colocated.

```bash
npm run test                  # Run all tests
npm run test -- --watch       # Watch mode
npm run test -- --coverage    # With coverage
```

### Test principles

- Test behavior, not implementation.
- Query by role/label (`getByRole`, `getByLabelText`), not by test-id.
- Use `test-id` only when no accessible query exists.

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserCard } from './UserCard';

test('displays user name and email', () => {
  render(<UserCard name="Alice" email="alice@test.com" role={UserRole.Admin} />);

  expect(screen.getByText('Alice')).toBeInTheDocument();
  expect(screen.getByText('alice@test.com')).toBeInTheDocument();
});
```

---

## Accessibility

- All interactive elements must be keyboard-accessible.
- Images require `alt` text.
- Form inputs require associated `<label>` elements.
- Use semantic HTML (`<nav>`, `<main>`, `<article>`, `<button>`) over generic `<div>`.
- `eslint-plugin-jsx-a11y` violations are errors, not warnings.

---

## API Communication

- Use a centralized API client in `lib/api-client.ts`.
- All API calls wrapped in React Query hooks inside `features/<name>/api.ts`.
- Never call `fetch` directly in components.

```tsx
// lib/api-client.ts
const BASE_URL = import.meta.env.VITE_API_URL;

export async function apiClient<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json() as Promise<T>;
}
```
