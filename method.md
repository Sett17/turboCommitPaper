# Methods

## Gathering Data

Several GitHub repositories were identified as suitable sources of commit messages.
These repositories include: taxonomy [@shadcnShadcnTaxonomy2023], demo-projects [@mot01FreeCodeCampDemoprojects2023], resume [@dcyouDcyouResume2022], and kotlin-faker [@serpro69Serpro69Kotlinfaker2023].
While kotlin-faker does not adhere to Conventional Commits, its commit messages maintain a consistent structure.
The specific functionality of these repositories is not vital for the evaluation.

All selected repositories have multiple contributors, which increases the diversity of the commit messages.
A Python script was utilized to traverse all commits in these repositories, extracting both the commit message and the corresponding git diff.
These data points were then stored in an SQLite database for further processing.
Commit messages authored by bots or merge commits were filtered out and placed in a separate table within the same SQLite database.

From the three repositories using Conventional Commits, slightly more than 100 non-filtered commits were collected for each (103 from taxonomy, 110 from demo-projects, and 127 from resume).
To maintain a balanced evaluation, only 113 random commits from kotlin-faker were included.
This approach ensures that the overall evaluation is not disproportionately influenced by the kotlin-faker repository.

## Implementation