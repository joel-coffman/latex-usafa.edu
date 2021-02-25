=========
promotion
=========

This package supports applications for academic promotion at the United States
Air Force Academy (USAFA). The package itself is effectively a "metapackage" to
avoid the need to know which package actually provides the various commands
used to typeset the application.

The promotion package includes the following packages:

record
  This package provides environments used to create the scholarship and service
  tables recommended by the Faculty Personnel Council (FPC) to document
  publications, presentations, and service for academic promotion. It
  reproduces the original Microsoft PowerPoint templates as faithfully as
  possible. The major advantages of using LaTeX are automatic citation
  formatting with BibTEX and automatic page breaks, specifically the ability to
  insert entries in reverse chronological order without manual moving existing
  entries to a new slide (i.e., page).

statement
  This package defines commands to format personal statements. Thus, it ensures
  consistent formatting for common elements.

supplements
  This package supports the inclusion of supplemental material into a larger
  document. For example, copies of publications can be included as
  supplementary material in an academic promotion package.
