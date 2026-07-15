// Vitest config for the tech-blog repo.
//
// Scope: only the JS regression tests under tests/js. The repo's primary test
// suite is Python (scripts/tests/) and is unaffected by this config.
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['tests/js/**/*.test.js'],
    // Installs a no-op Element.prototype.scrollIntoView so leaked setTimeout
    // callbacks (which jsdom cannot satisfy) never throw an unhandled error
    // that flakes the whole run to exit 1. See tests/js/setup.js.
    setupFiles: ['tests/js/setup.js'],
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
      // measured 2026-07-10 baseline (branch 69.5 / stmt 86.7 / func 89.3 /
      // line 86.8, after dead-code removal + coverage boosts) so ordinary noise
      // from the new-Function eval merge does not flake CI, while a real
      // coverage drop fails `npm run test:coverage`.
      // Raise these as coverage improves; never lower to make a red build pass.
      thresholds: {
        branches: 62,
        functions: 82,
        lines: 80,
        statements: 80,
      },
    },
  },
});
