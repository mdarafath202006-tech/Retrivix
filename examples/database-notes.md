# Database storage notes

A database storage engine maps logical records to physical pages. A write-ahead log records intended changes before data pages are updated, allowing recovery after an interrupted write.

# Search engine notes

An inverted index maps each term to documents containing that term. BM25 ranks documents using term frequency, inverse document frequency, and document length normalization.

# Offline-first systems

Offline-first applications keep core data and behavior available without network access. Synchronization can happen later when a connection returns.