module.exports = {
  multipass: true,
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // Preserve HQ marker HTML comments
          removeComments: false,
          // Preserve linearGradient IDs (bgSpread, heroPanel, sgArrow, etc.)
          cleanupIds: false,
          // More aggressive numeric precision (was 2, now 1)
          cleanupNumericValues: { floatPrecision: 1 },
          // Enable path merging for non-text elements
          mergePaths: true,
          // Enable path data conversion for size reduction
          convertPathData: { floatPrecision: 1 },
          // Keep transforms for text alignment safety
          convertTransform: false,
        }
      }
    },
    { name: 'removeUnusedNS' },
    { name: 'removeXMLProcInst' },
  ]
}
