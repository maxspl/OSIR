<script setup lang="ts">
const items = [
  {
    label: 'Orchestration',
    icon: 'i-lucide-workflow',
    children: [
      {
        label: 'Profile & Modules',
        description: 'Execute Profile & Modules on case',
        icon: 'i-lucide-layers',
        to: '/cases'
      },
      {
        label: 'File & Folder',
        description: 'Execute modules on file or folder',
        icon: 'i-lucide-folder-open',
        to: '/files'
      }
    ]
  },
  {
    label: 'Monitoring',
    icon: 'i-lucide-monitor-dot',
    children: [
      {
        label: 'Task On-Going',
        description: 'Find and monitor your on-going tasks',
        icon: 'i-lucide-list-checks',
        to: '/monitoring/tasks'
      },
      {
        label: 'Orchestration',
        description: 'Find and monitor your on-going handlers',
        icon: 'i-lucide-activity',
        to: '/monitoring/orchestration'
      },
      {
        label: 'Flower',
        description: 'Monitor your agent & master using Flower',
        icon: 'i-lucide-cpu',
        to: '/monitoring/flower'
      }
    ]
  },
  {
    label: 'Docs',
    icon: 'i-lucide-book-open',
    children: [
      {
        label: 'OSIR Docs',
        description: 'Global documentation of OSIR',
        icon: 'i-lucide-file-text',
        to: '/docs/osir'
      },
      {
        label: 'API Docs',
        description: 'Interactive Fast API documentation',
        icon: 'i-lucide-code-2',
        to: '/docs/api'
      },
      {
        label: 'Module & Profile',
        description: 'Read the configuration of modules and profiles',
        icon: 'i-lucide-life-buoy',
        to: '/helper'
      }
    ]
  },
  {
    label: 'Report Bug',
    icon: 'i-lucide-bug',
    to: 'https://github.com',
    target: '_blank'
  }
]
</script>

<template>
  <UNavigationMenu :items="items" />
</template>
