/**
 * src/api.js — re-exports from the canonical service layer.
 * Import directly from src/services/api.js in new code.
 * This shim exists only for backwards-compat with any legacy imports.
 */
export {
  checkHealth,
  fetchHealth,
  getCategories,
  fetchCategories,
  searchKnowledge,
  search,
  getDocumentSections,
  fetchDocumentSections,
  getDocuments,
  uploadDocument,
  deleteDocument,
} from './services/api'
