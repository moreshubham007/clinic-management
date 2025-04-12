#!/bin/bash

# Remove unnecessary files
rm -rf app/(tabs)/explore.tsx
rm -rf components/Collapsible.tsx
rm -rf components/ExternalLink.tsx
rm -rf components/HelloWave.tsx
rm -rf components/ParallaxScrollView.tsx
rm -rf components/ui

# Create necessary directories
mkdir -p src/{api,components,hooks,constants,screens,utils}

# Create base files
touch src/api/index.ts
touch src/components/index.ts
touch src/hooks/index.ts
touch src/constants/index.ts
touch src/screens/index.ts
touch src/utils/index.ts 