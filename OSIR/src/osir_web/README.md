# OSIR Web Package

The `osir_web` package is the web UI of OSIR (Open Source Incident Response). It is a Nuxt application that lets analysts manage cases, run modules and profiles, browse case files and monitor processing — talking to the OSIR API served by the master.

## Overview

OSIR Web provides:

- **Case orchestration** — create cases, run a profile or a selection of modules on a case, edit module YAML configurations inline
- **File orchestration** — browse the case directory tree, run modules on individual files or folders, upload files (Uppy + Tus resumable uploads)
- **Monitoring** — follow ongoing tasks, handlers and orchestration status, Celery workers through Flower, and system status
- **Helper** — inspect the YAML configuration of any profile or module
- **Docs** — embedded documentation pages, including the API documentation

## Tech Stack

- **Nuxt 4 / Vue 3** — application framework
- **Nuxt UI v4 + Tailwind CSS 4** — interface components and styling
- **Pinia** — state management (case, handler, module, profile, task, flower, auth stores)
- **Monaco Editor** — YAML editing of module configurations
- **VueFinder** — file explorer
- **Uppy (Tus)** — resumable file uploads
- **highlight.js** — log and content highlighting

## Package Structure

```
osir_web/
├── app/
│   ├── api/                # API client layer (case, files, handler, module, profile, system, tasks)
│   ├── assets/             # Styles and static assets
│   ├── components/         # UI components (OsirHeader, OsirMenu, TreeSelector, YamlEditor, ...)
│   ├── composables/        # Shared Vue composables
│   ├── pages/              # Application pages (cases, files, helper, monitoring, docs, ...)
│   ├── plugins/            # Nuxt plugins
│   ├── stores/             # Pinia stores
│   └── utils/              # Utility functions
├── nuxt.config.ts          # Nuxt configuration
└── public/                 # Public static files
```

## Architecture

The application listens on port **8501** and proxies API requests to the OSIR
FastAPI backend (`master-api:8502`):

```
Browser ──► osir_web (8501) ──► /proxy/** ──► OSIR API (8502)
```

## Development

```bash
cd osir_web

# Install dependencies
pnpm install

# Start the development server (http://localhost:8501)
pnpm dev

# Production build
pnpm build

# Lint and type checking
pnpm lint
pnpm typecheck
```

The API base URL can be adapted through the Nuxt runtime configuration; by
default API calls go through the `/proxy` route of the development server.

## Deployment

In production the application is built and served as part of the OSIR master
stack, alongside the FastAPI backend and the other OSIR containers (see the
main OSIR documentation for the `osir-launcher.py` workflow).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
