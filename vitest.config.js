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
    coverage: {
      // The source under test is executed via `new Function(source)` inside each
      // test (see tests/js/*.test.js). v8 only attributes that eval'd code to a
      // file when the source carries a `//# sourceURL=` trailer, which the test
      // loaders append. Without it, coverage reports a misleading 0%.
      provider: 'v8',
      include: ['assets/js/**/*.js'],
      reporter: ['text', 'json-summary'],
      // Regression floor (global aggregate). Set a few points below the
      // measured 2026-07-10 baseline (branch 62.4 / stmt 79.2 / func 83.4 /
      // line 79.7) so ordinary noise from the new-Function eval merge does not
      // flake CI, while a real coverage drop fails `npm run test:coverage`.
      // Raise these as coverage improves; never lower to make a red build pass.
      thresholds: {
        branches: 55,
        functions: 75,
        lines: 72,
        statements: 72,
      },
    },
  },
});
