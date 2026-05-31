import type { TreeItem } from '@nuxt/ui'

// ── Helper: Sort children - nodes with children come first ────────────

function sortChildren(children: TreeItem[] | undefined): TreeItem[] | undefined {
  if (!children || children.length === 0) return children
  return [...children].sort((a, b) => {
    const hasChildrenA = !!a.children && a.children.length > 0
    const hasChildrenB = !!b.children && b.children.length > 0
    if (hasChildrenA && !hasChildrenB) return -1
    if (!hasChildrenA && hasChildrenB) return 1
    return 0
  })
}

function sortTreeNodes(nodes: TreeItem[] | undefined): TreeItem[] | undefined {
  if (!nodes) return nodes

  // 1. Récursion d'abord sur les enfants
  const withSortedChildren = nodes.map(node => ({
    ...node,
    children: sortTreeNodes(node.children),
  }))

  // 2. Ensuite on trie ce niveau
  return sortChildren(withSortedChildren)
}

// ── Helper: Build tree from module paths ────────────────────────────────
export function buildTreeFromPaths(paths: string[]): TreeItem[] {
  const categorizedPaths = paths.filter(p => p.includes('/'))
  const basicPaths = paths.filter(p => !p.includes('/'))

  // Track all labels globally across the entire tree to detect duplicates
  const allLabels = new Set<string>()

  // Build categorized tree
  const categorized: TreeItem[] = []
  if (categorizedPaths.length > 0) {
    const root: TreeItem = { label: 'root', value: 'root', children: [] }

    for (const path of categorizedPaths) {
      const parts = path.split('/')
      let current = root

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i]
        
        const existing = current.children?.find(c => c.label === part)

        if (existing) {
          current = existing
        } else {
          const isLeaf = i === parts.length - 1
          let finalLabel = part
          
          // Check if this label already exists anywhere in the tree
          if (allLabels.has(part)) {
            // Append parent name in parentheses
            finalLabel = `${part} (${current.label})`
          }
          
          allLabels.add(finalLabel)
          
          const node: TreeItem = {
            label: finalLabel,
            value: path,
            children: isLeaf ? undefined : [],
          }
          // Vérifier que finalLabel n'existe pas déjà comme enfant de current
          const finalLabelExists = current.children?.some(c => c.label === finalLabel)
          if (!finalLabelExists) {
            if (current.children) {
              current.children.push(node)
            } else {
              current.children = [node]
            }
            current = node
          } else {
            // Si finalLabel existe déjà, utiliser le nœud existant
            current = current.children!.find(c => c.label === finalLabel)!
          }
        }
      }
    }

    if (root.children) {
      categorized.push(...root.children)
    }
  }

  // Build Basic category
  const basic: TreeItem[] = []
  if (basicPaths.length > 0) {
    basic.push({
      label: 'Basic',
      value: 'basic',
      children: basicPaths.map(p => ({
        label: p,
        value: p,
      })),
    })
  }

  // Sort all tree nodes: children with their own children come first
  const sortedBasic = sortTreeNodes(basic)
  const sortedCategorized = sortTreeNodes(categorized)
  console.log(sortedCategorized)
  return [...(sortedBasic || []), ...(sortedCategorized || [])]
}
