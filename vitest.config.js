// Vitest config for the tech-blog repo.
//
// Scope: only the JS regression tests under tests/js. The repo's primary test
// suite is Python (scripts/tests/) and is unaffected by this config.
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['tests/js/**/*.test.js'],
    globals: false,
  },
});
